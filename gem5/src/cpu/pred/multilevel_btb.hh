#ifndef __CPU_PRED_MULTILEVEL_BTB_HH__
#define __CPU_PRED_MULTILEVEL_BTB_HH__

#include "base/cache/associative_cache.hh"
#include "cpu/pred/conditional.hh"
#include "cpu/pred/btb.hh"
#include "cpu/pred/btb_entry.hh"
#include "mem/cache/tags/tagged_entry.hh"
#include "params/MultiLevelBTB.hh"
#include <unordered_set>
#include <queue>
#include <vector>

namespace gem5::branch_prediction
{


class MultiLevelBTB : public BranchTargetBuffer
{
  public:
    MultiLevelBTB(const MultiLevelBTBParams &params);

    void memInvalidate() override;
    bool valid(ThreadID tid, Addr instPC) override;

    const PCStateBase *lookup(ThreadID tid, Addr instPC,
                              BranchType type = BranchType::NoBranch) override;

    BTBLookupResult lookupWithLatency(ThreadID tid, Addr instPC,
                                      BranchType type = BranchType::NoBranch,
                                      bool taken = true,
                                      Addr blockStartAddr = 0,
                                      bool basePrediction = true) override;

    Addr lookupL1(ThreadID tid, Addr instPC) override;

    void recordBTBAccess(BTBAccessLevel level,
                         BTBAccessReason reason = NoReason) override;

    void update(ThreadID tid, Addr instPC, const PCStateBase &target_pc,
                BranchType type = BranchType::NoBranch,
                StaticInstPtr inst = nullptr) override;

    void updateDirection(ThreadID tid, Addr inst_pc, bool taken) override;

    const StaticInstPtr getInst(ThreadID tid, Addr instPC) override;

    void setBranchPredictor(ConditionalPredictor *cp) { cPred = cp; }

    void setBBMap(const std::unordered_map<Addr, Addr> *map) { bbMap_ = map; }

    void trainMarkovOnCommit(ThreadID tid, Addr pc, bool wasL2Hit);
    void trainPrefetchBitsOnCommit(ThreadID tid, Addr pc, bool actuallyTaken, BranchType type);

    void startup() override;

  private:
    ConditionalPredictor *cPred = nullptr;
    const std::unordered_map<Addr, Addr> *bbMap_ = nullptr;

    AssociativeCache<BTBEntry> l1btb;

    AssociativeCache<BTBEntry> pBuffer;

    AssociativeCache<BTBEntry> l2btb;
    AssociativeCache<BTBEntry> l3btb;

    const Cycles l1Latency;
    const Cycles l2Latency;
    const Cycles l3Latency;
    const bool enableL3;
    const unsigned minInstSize;
    const bool trainBitsOnLookup;
    const bool trainBitsOnCommit;
    const bool prefetchOnPrefetchHit;
    const bool cleanBitsOnL1Promotion;
    const bool noPrefetchLatency;
    const unsigned prefetchDepth;
    const unsigned maxChainTrackerEntries;
    const bool depthOnlyCall;
    const bool limitRet;
    const bool markovUseRecency;
    const bool nonexclusive;
    const bool newPBits;
    const bool onlyCall;
    const bool onlyCallAndBackward;
    const bool callFallthrough;
    const bool forwardLoopExit;
    const bool backwardLoopExit;
    const bool allConditional;
    const bool prefetchFwExitOnL1Hit;
    const bool useCompressedTagFilter;
    const bool indirectAltBit;




    // Multi-level BTB specific statistics
    struct MultiLevelBTBStats : public statistics::Group
    {
        MultiLevelBTBStats(statistics::Group *parent, MultiLevelBTB *btb);

        void preDumpStats() override;
        //For exploring the 1-history Markov prefetcher:
        //If branch A misses in L1BTB1(hits in L2BTB),
        //then the immediate branch B is the successor of A if B also misses in L1BTB2 (hits in L2BTB2).
        statistics::SparseHistogram successorCountDist;
        statistics::SparseHistogram markovDist;

        statistics::Scalar l1MissL2Hits;
        statistics::Scalar l1Hits;
        statistics::Scalar normalL1Hits;
        statistics::Scalar l1Accesses;
        statistics::Scalar l2Accesses;
        statistics::Vector l2AccessesByReason;
        statistics::Scalar l1HitInOverriding;
        statistics::Scalar l1MissInOverriding;
        statistics::Scalar pbHits;
        statistics::Scalar l3Hits;
        statistics::Vector uselessPrefetches;
        statistics::Scalar totalPrefetches;
        statistics::Scalar prefetchQueueFull;

        // Unified prefetch coverage: pBuffer hits + L1 reuse
        statistics::Vector prefetchHits;            // pBuffer hit + L1 reuse (both are useful)
        statistics::Vector latePrefetchByPBHit;
        statistics::Vector latePrefetchByL2Hit;
        statistics::Formula prefetchCoverage;       // prefetchHits / (prefetchHits + totalPrefetches)

        // Separate useless rates for pBuffer and L1
        statistics::Formula pBufferUselessRate;     // uselessPrefetches / totalPrefetches

        statistics::Scalar l1InstalledEvicted;   // L1 evictions of pBuffer-installed entries without reuse
        statistics::Scalar l1Installed;             // count of entries installed from pBuffer to L1
        statistics::Formula l1UselessInstalledRate;  // l1InstalledEvicted / l1Installed

        // For TAGE prediction
        // statistics::Scalar predMatches;
        // statistics::Scalar predChecks;
        statistics::Vector predMatches;
        statistics::Vector predChecks;
        statistics::Formula predMatchRatio;

        // Evaluate the false positive rate of compressed tag array
        statistics::Scalar compressedTagChecks;
        statistics::Scalar compressedTagFalsePositives;
        statistics::Formula compressedTagFalsePositiveRate;

        // the false negative rate
        statistics::Scalar compressedTagFalseNegatives;
        statistics::Formula compressedTagFalseNegativeRate;

        // alias counter
        statistics::Scalar compressedTagAliases;

        // Prefetch direction counts
        statistics::Scalar takenPathPrefetches;     // prefetches triggered by prefetchTarget bit
        statistics::Scalar notTakenPathPrefetches;  // prefetches triggered by prefetchThrough bit
        statistics::Vector prefetchHitsFromTaken;
        statistics::Vector prefetchHitsFromNotTaken;

        // Call fall-through coverage stats
        statistics::Scalar callL2OrPrefetchHits;    // Calls that hit in L2 or prefetched
        statistics::Scalar callFallThroughL2Only;    // of those, fall-through branch only in L2
        statistics::Formula callFallThroughL2Ratio;  // callFallThroughL2Only / callL2OrPrefetchHits

        statistics::Scalar updatesL1hits;  // branch not in L1 at commit, found in L2
        statistics::Scalar updatesL2hits;  // branch not in L1 at commit, found in L2
        statistics::Scalar updatesL2miss;  // branch not in L1 at commit, found in L2

        statistics::Scalar updatesL3hits;  // branch not in L1 at commit, found in L3
        statistics::Scalar updatesL3miss;  // branch not in L1 at commit, found in L3

        statistics::Scalar pfIssued;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfL2LookupHit;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfL2LookupMiss;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfL3LookupHit;  // L2 miss but L3 hit in deferred prefetch queue
        statistics::Scalar pfL3LookupMiss;  // L2 miss but L3 hit in deferred prefetch queue
        statistics::Scalar mkHits;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfTriggerCall;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfTriggerBwExit;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfTriggerFwExit;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfTriggerCondAlt;  // branch not in L1 at commit, found in L2
        statistics::Scalar pfInserted;  // branch not in L1 at commit, found in L2

        statistics::Scalar skipDuetoDemand;
        statistics::Scalar skipDuetoPresence;
        statistics::Scalar enqueueDeferred;
        statistics::Formula skipDuetoDemandRatio;
        statistics::Formula skipDuetoPresenceRatio;

        // Chain early termination reason stats
        statistics::Scalar chainEndEvicted;      // chain slot evicted by newer chain
        statistics::Scalar chainEndDemand;        // chain killed by demand access
        statistics::Scalar chainEndPresence;      // chain killed by L1/PB hit
        statistics::Scalar chainEndL2Miss;        // chain step failed due to L2 miss
        statistics::Scalar chainEndL3Miss;        // chain step failed due to L3 miss
        statistics::Scalar chainEndRetFilter;     // chain step filtered by limitRet
        statistics::Scalar chainEndNonEntry;
        statistics::Scalar chainEndDepthExhaust;  // chain reached remaining depth 0 naturally

        statistics::Distribution prefetchesPerTrigger;
        statistics::Distribution parallelChains;

        MultiLevelBTB *btb;

    } multilevelstats;
    // Markov prefetcher data structure
    // key: branch PC (L1 miss, L2 hit)
    // value: map of successor PC -> access frequency
    std::unordered_map<Addr, std::unordered_map<Addr, uint64_t>> markovSuccessors;

    struct MarkovEntry : public TaggedEntry
    {
        /** vector containing the state of the cachelines in this zone */
        std::vector<std::pair<Addr, uint64_t>> successors;

        MarkovEntry(size_t num_entries, TagExtractor ext)
          : TaggedEntry()
        {
            registerTagExtractor(ext);
        }

        void
        invalidate() override
        {
            TaggedEntry::invalidate();
            successors.clear();
        }
    };

    const bool limitedMarkov;
    const bool markovOnlyMisses;
    const int maxMarkovSuccessors;
    AssociativeCache<MarkovEntry> markov;

    std::queue<std::pair<Addr, bool>> prevBranches;

    // tacking the previous branch PC for each thread.
    std::vector<Addr> prevBranchPC;

    // trainBitsOnLookup: per-thread tracking of previous block info for lookup training
    struct PrevBlockInfo {
        Addr branchPC = 0;
        Addr target = 0;
        Addr fallThrough = 0;
        bool valid = false;
    };
    std::vector<PrevBlockInfo> prevBlockInfo;

    // Deferred prefetch queue: stages prefetches by issueTime before inserting into pBuffer.
    struct DeferredPrefetchEntry {
        Addr pc = 0;
        ThreadID tid = 0;
        Cycles issueTime = Cycles(0);
        bool toL1 = false;
        bool triggeredByPBHit = false;
        bool takenPrefetched = false;
        BranchType triggerType = BranchType::NoBranch;
        uint64_t chainId = 0;
        bool allocateChain = false;
        unsigned depth = 0;
    };
    std::vector<DeferredPrefetchEntry> deferredPrefetchQueue;
    uint64_t nextChainId = 1;

    enum class ChainEndReason {
        None = 0,
        Evicted,        // chain slot evicted by newer chain
        Demand,         // chain killed by demand access
        Presence,       // chain killed by L1/PB hit
        L2Miss,         // L2 miss for prefetch target
        L3Miss,         // L3 miss for prefetch target
        RetFilter,      // filtered by limitRet (Return type)
        DepthExhaust,   // remaining depth reached 0 naturally
    };

    struct ActiveChainEntry {
        uint64_t chainId = 0;
        unsigned remainingPrefetches = 0;
        ChainEndReason lastEndReason = ChainEndReason::None;
    };
    std::vector<ActiveChainEntry> chainTable;

    /** Check if chain has no more in-flight entries and record end reason. */
    bool isChainDead(uint64_t chainId) const;
    void recordChainEnd(ActiveChainEntry &chain);

    std::unordered_set<Addr> currentCycleDemand;

    void recordDemandLookup(Addr pc) {
        currentCycleDemand.insert(pc);
    }

    bool isDemandAccess(Addr pc) const {
        return currentCycleDemand.find(pc) != currentCycleDemand.end();
    }

    friend struct MultiLevelBTBStats;

    /**
     * Handle L1 BTB hit.
     * Handles prefetched entry hits and prediction match checking.
     */
    BTBLookupResult handleL1Hit(ThreadID tid, Addr instPC, BTBEntry *l1_entry,
                                BranchType type, bool taken, bool basePrediction);

    /**
     * Handle pBuffer hit.
     * Promotes entry from pBuffer to L1 and tracks statistics.
     */
    BTBLookupResult handlePBufferHit(ThreadID tid, Addr instPC,
                                     BTBEntry *pB_entry, BranchType type,
                                     bool taken, bool basePrediction);

    /**
     * Handle L2 BTB hit.
     * Inserts the entry into L1 and triggers configured prefetchers.
     */
    BTBLookupResult handleL2Hit(ThreadID tid, Addr instPC, BTBEntry *l2_entry,
                                BranchType type, bool taken);

    BTBLookupResult handleL3Hit(ThreadID tid, Addr instPC, BTBEntry *l3_entry,
                                BranchType type, bool taken);

    /**
     * Prefetch the most frequent Markov successors of a given PC.
     * @param numSuccessors Number of top successors to prefetch (default 1)
     */
    void prefetchMarkovSuccessor(ThreadID tid, Addr pc, bool toL1,
                                 unsigned numSuccessors = 1,
                                 bool triggeredByPBHit = false,
                                 Cycles baseLatency = Cycles(0), BranchType triggerType = BranchType::NoBranch, int depth=1);

    // For L1 prefetcher's bandwidth issue.
    AssociativeCache<BTBEntry> l1CompressedTags;
    AssociativeCache<BTBEntry> pbCompressedTags;

    bool l1ApproxContains(Addr pc, ThreadID tid);
    bool pbApproxContains(Addr pc, ThreadID tid);

    enum class TagAction { Hit, Insert, Invalidate };
    void l1CompressedTagSync(Addr pc, ThreadID tid, TagAction action);
    void pbCompressedTagSync(Addr pc, ThreadID tid, TagAction action);

    /** Process deferred prefetches whose issueTime has passed. */
    void processDeferredPrefetchQueue();
    EventFunctionWrapper pfqEvent;

    /** Enqueue a prefetch into the in-flight queue. */
    void enqueuePrefetch(Addr pc, ThreadID tid, BTBEntry *l2_entry,
                         Cycles arrivalCycle, bool toL1,
                         bool triggeredByPBHit, uint8_t pfDistance = 0,
                         bool takenPrefetched = false,
                         BranchType triggerType = BranchType::NoBranch,
                         bool fromL3 = false);


    /** Returns true for policies that use prefetch-bit logic. */
    bool usesPrefetchBitPolicy() const;

    bool isCall(BranchType type) const {
        return type == BranchType::CallDirect || type == BranchType::CallIndirect;
    }

    struct PrevBrInfo {
        bool is_bw;
        bool is_l1_miss;
    } prevBwBranch;

    enum TriggerLocation { L1Hit, L2Hit, L3Hit, PBHit };
    void applyNewPBitsLogic(BranchType type, bool taken,
                            bool isBackward,
                            bool &doPfTarget, bool &doPfThrough,
                            TriggerLocation triggerLoc);

    /** Evict an L1 victim entry to L2, writing back full state. */
    void writebackToL2(ThreadID tid, BTBEntry *victim);

    BTBEntry* freeUpL1Entry(ThreadID tid, Addr instPC);

    /** Record previous block info for next-iteration training. */
    void recordPrevBlockInfo(ThreadID tid, Addr instPC, Addr targetAddr);

    /**
     * Prefetch a successor branch via bbMap lookup → pBuffer insertion.
     * @param lookupAddr  Address to look up in bbMap (target or fallThrough).
     * @param isTakenPath true → takenPathPrefetches stat; false → notTakenPathPrefetches.
     * @param baseLatency Cumulative latency for depth > 1 prefetches.
     */
     void prefetchViaBBMap(ThreadID tid, Addr lookupAddr, bool isTakenPath,
                           bool triggeredByPBHit, int depth=1,
                           Cycles baseLatency = Cycles(0),
                           BranchType triggerType = BranchType::NoBranch,
                           uint64_t chainId = 0,
                           bool allocateChain = false);

    /**
     Try triggering a initial prefetch.
     */
    void tryInitialTrigger(ThreadID tid, Addr instPC, BranchType type,
                          Addr targetAddr, bool doPfTarget, bool doPfThrough,
                          bool taken, TriggerLocation triggerLoc,
                          Cycles baseLatency, bool triggeredByPBHit,
                          bool isL1Miss);

};
} // namespace gem5::branch_prediction

#endif // __CPU_PRED_MULTILEVEL_BTB_HH__
