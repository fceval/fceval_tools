# visualizer
1,to visualize the overall coverage information and that of base fuzzers, we send this information by  Statsd protocol when scheduler running. This routine is implemented in the framework with Rust language. See  fceval_main/framework/src/scheduler/casefc.rs

2, to visulaize the fuzzing states of base fuzzers , we plant this function from AFL++ and need to modify the source codes of them.  See fceval_main/docker/system/afl-2.56b.tar.gz or aflplusplus_3.11c.tar.gz

3,we could see the above information on the Webpage on the fly.
