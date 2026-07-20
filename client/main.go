package main

import (
	"bytes"
	"flag"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"text/template"
	"time"

	log "github.com/sirupsen/logrus"
)

var (
	url  = flag.String("url", "0.0.0.0", "The url to connect to")
	port = flag.String("port", "9999", "the port to connect to")
	// input       = flag.String("input", defaultInput, "Input to the function")
	file        = flag.String("f", "", "Pass in a template file with a list of urls")
	concurrency = flag.Int("c", 1, "Number of concurrent requests")
	numInvoke   = flag.Int("n", 10, "Number of invocations")
	numWarm     = flag.Int("w", 0, "Number of invocations for warming")
	delay       = flag.Int("delay", 0, "Add a delay between sending requests (us)")
	logfile     = flag.String("logging", "", "Log to file instead of standart out")
	m5_enable   = flag.Bool("m5ops", false, "Enable m5 magic instructions")
	m5_interval = flag.Int("m5iv", 0, "Invertal to issue a m5 workend instruction")
	verbose     = flag.Bool("v", false, "Print verbose output")
	mulitclient = flag.Bool("mulitclient", false, "Print verbose output")

	// Client
	_client    *http.Client
	requestURL = ""
	_measure   = false
)

func main() {
	flag.Parse()

	// open file and create if non-existent
	if *logfile != "" {
		file, err := os.OpenFile(*logfile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatal(err)
		}
		defer file.Close()
		log.SetOutput(file)
	}

	if *verbose {
		log.SetLevel(log.DebugLevel)
	} else {
		log.SetLevel(log.InfoLevel)
	}

	requestURL = fmt.Sprintf("http://%s:%s", *url, *port)
	log.Printf("Start client: %s, Requests: %d, Concurrency: %d\n", requestURL, *numInvoke, *concurrency)

	// Create the warmup jobs and run jobs
	wjobs := makeJobs(*numWarm)
	rjobs := makeJobs(*numInvoke)

	// Create the client
	if !*mulitclient {
		_client = httpClient()
	}
	// client := nil

	start := time.Now()
	r, nb := runJobs(_client, wjobs, true)

	str := fmt.Sprintf("\nWarmup requests:\t %d/%d\n", r, *numWarm)
	str += fmt.Sprintf("Data transfered:\t %fMB\n", float64(nb)/1024/1024)
	str += fmt.Sprintf("Time elapsed:\t\t %f sec.\n", time.Since(start).Seconds())
	str += fmt.Sprintf("Transaction rate:\t %f trans/s\n", float64(r)/time.Since(start).Seconds())
	str += fmt.Sprintf("Throughput:\t\t %f MB/s\n", float64(nb)/1024/1024/time.Since(start).Seconds())
	log.Println(str)

	time.Sleep(1 * time.Second)
	// Run the actual jobs
	if *m5_enable {
		cmd := exec.Command("/usr/local/bin/m5", "fail", "4")
		cmd.Run()
	}
	start = time.Now()
	r, nb = runJobs(_client, rjobs, false)

	str = fmt.Sprintf("\nMeasure requests:\t %d/%d\n", r, *numWarm)
	str += fmt.Sprintf("Data transfered:\t %fMB\n", float64(nb)/1024/1024)
	str += fmt.Sprintf("Time elapsed:\t\t %f sec.\n", time.Since(start).Seconds())
	str += fmt.Sprintf("Transaction rate:\t %f trans/s\n", float64(r)/time.Since(start).Seconds())
	str += fmt.Sprintf("Throughput:\t\t %f MB/s\n", float64(nb)/1024/1024/time.Since(start).Seconds())
	log.Println(str)

}

type Job struct {
	url   string
	post  bool
	input string
}

func invoke(client *http.Client, job Job) (int, error) {

	var req *http.Request
	var err error
	if job.post {
		req, err = http.NewRequest(http.MethodPost, job.url, bytes.NewBuffer([]byte(job.input)))
		req.Header.Set("X-Custom-Header", "myvalue")
		log.Debugf("POST: %s -> %s\n", job.url, job.input)
	} else {
		req, err = http.NewRequest(http.MethodGet, job.url, nil)
	}

	if err != nil {
		log.Fatalf("client: could not create request: %s\n", err)

	}
	req.Header.Set("Content-Type", "application/json")

	res, err := client.Do(req)
	if err != nil {
		// log.Fatalf("client: error making http request: %s\n", err)
		return -1, err
	}

	resBody, err := ioutil.ReadAll(res.Body)
	res.Body.Close()

	if err != nil {
		// log.Fatalf("client: could not read response body: %s\n", err)
		return -1, err
	}
	// fmt.Printf("client: response body: %s\n", resBody)
	if res.StatusCode != http.StatusOK {
		log.Warnf("GET: %s -> resp: %d\n", job.url, res.StatusCode)
	} else {
		log.Debugf("GET: %s -> resp: %d, %d\n", job.url, res.StatusCode, len(resBody))
	}

	return len(resBody), nil
}

func httpClient() *http.Client {
	client := &http.Client{
		Transport: &http.Transport{
			MaxIdleConnsPerHost: 20,
			MaxConnsPerHost:     20,
		},
		Timeout: 10 * time.Second,
	}

	return client
}

// Here's the worker, of which we'll run several
// concurrent instances. These workers will receive
// work on the `jobs` channel and send the corresponding
// results on `results`.
func worker(client *http.Client, jobs []Job, results chan<- int) {
	if client == nil {
		client = httpClient()
	}
	for _, j := range jobs {
		res, _ := invoke(client, j)
		results <- res
	}
}

func runJobs(client *http.Client, jobs []Job, warming bool) (int, int) {

	// In order to use our pool of workers we need to send
	// them work and collect their results. We make 2
	// channels for this.
	numJobs := len(jobs)
	results := make(chan int, numJobs)

	// This starts up 3 workers, initially blocked
	// because there are no jobs yet.
	step := numJobs / *concurrency
	if numJobs%*concurrency != 0 {
		log.Fatalf("Number of jobs (%d) must be a multiple of the concurrency (%d)\n", numJobs, *concurrency)
	}
	for w := 0; w < *concurrency; w++ {
		wjobs := jobs[w*step : (w+1)*step]
		go worker(client, wjobs, results)
	}

	// Finally we collect all the results of the work.
	// This also ensures that the worker goroutines have
	// finished. An alternative way to wait for multiple
	// goroutines is to use a [WaitGroup](waitgroups).
	succesful := 0
	nbytes := 0
	for a := 1; a <= numJobs; a++ {
		r := <-results
		if r > 0 {
			succesful++
			nbytes += r
		}
		if numJobs > 10 && a%(numJobs/10) == 0 {
			log.Printf("Progress: %d/%d\n", a, numJobs)
		}
		if !warming && *m5_enable && *m5_interval > 0 && a%*m5_interval == 0 {
		}
	}
	return succesful, nbytes
}

func makeJobs(numJobs int) (jobs []Job) {

	if *file != "" {

		sampleJobs := parserTemplate(*file)
		for j := 1; j <= numJobs; j++ {

			job := sampleJobs[rand.Intn(len(sampleJobs))]

			// The input may contain a RAND function
			// e.g. RANDINT will generate a random integer
			if strings.Contains(job.input, "RANDINT") {
				v := rand.Intn(1000000)
				job.input = strings.Replace(job.input, "RANDINT", fmt.Sprintf("%d", v), -1)
			}
			jobs = append(jobs, job)

		}
	} else {

		for j := 1; j <= numJobs; j++ {
			jobs = append(jobs, Job{requestURL, false, ""})
		}
	}
	return
}

func parserTemplate(file string) []Job {
	// variables
	vars := make(map[string]interface{})
	vars["PORT"] = *port
	vars["HOST"] = *url
	vars["PROT"] = "http"

	// parse the template
	tmpl, err := template.ParseFiles(file)
	if err != nil {
		log.Fatalf("client: could not parse template: %s\n", err)
	}

	// create a new file
	var tpl bytes.Buffer

	// apply the template to the vars map and write the result to file.
	tmpl.Execute(&tpl, vars)

	lines := strings.Split(tpl.String(), "\n")
	// remove empty lines
	for i := len(lines) - 1; i >= 0; i-- {
		if lines[i] == "" {
			lines = append(lines[:i], lines[i+1:]...)
		}
	}

	var jobs []Job
	for _, line := range lines {

		if strings.Contains(line, "|>") {
			// |> is the delimiter for a post request
			// split the line into url and input
			tmp := strings.Split(line, "|>")
			url := tmp[0]
			input := tmp[1]

			jobs = append(jobs, Job{url, true, input})
		} else {
			jobs = append(jobs, Job{line, false, ""})
		}
	}
	return jobs
}
