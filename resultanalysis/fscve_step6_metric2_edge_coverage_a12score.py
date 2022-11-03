import pandas as pd
# calculate tables of edge coverage
expids = 20  #repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}
fcs = {"fca", "fcb"}

def a12(lst1,lst2,rev=True):
    """how often is x in lst1 more than y in lst2?"""
    more = same = 0.0
    for x in lst1:
        for y in lst2:
            if   x==y : same += 1
            elif rev     and x > y : more += 1
            elif not rev and x < y : more += 1
    return (more + 0.5*same)  / (len(lst1)*len(lst2))

for bm in benchmarks:
    dffca = pd.read_csv(f"csv/fscve_edge_count_global_results_{bm}_fca.csv")
    list_exp = []
    for i in range(1,expids+1):
        list_exp.append(f"experiment_id_{i}")
    lista = dffca.loc[0,list_exp].values
    dffcb = pd.read_csv(f"csv/fscve_edge_count_global_results_{bm}_fcb.csv")
    listb = dffcb.loc[0,list_exp].values
    print(f"{bm} edge counts a12 score fca>fcb")
    print(a12(lista,listb,rev=True))
    dict_value_benchmark = [f"{bm}"]
    dict_value_a12 = [f"{a12(lista,listb,rev=True)}"]

    dictca = {"benchmark":dict_value_benchmark, "a12":dict_value_a12}
    dfres = pd.DataFrame(dictca)
    #print(df_unique_crashes)
    dfres.to_csv(f"csv/fscve_step6_metric2_edge_coverage_a12score_{bm}.csv")
    print("***"*20)
