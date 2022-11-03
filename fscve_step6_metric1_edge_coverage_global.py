import pandas as pd

# calculate tables of edge coverage
benchmark = "nm"
expids = 20  # repeated times
benchmarks = {"cflow", "jq", "mp42aac", "nm", "objdump", "readelf", "libpng", "libxml2", "openssl", "lua"}  # "exiv2",
fcs = {"fca", "fcb"}
# calc the final results of global edge coverage for repeaded experiments
# out csv tables
dfs = []
for bm in benchmarks:
    df = pd.read_csv(f"csv/fscve_edge_count_global_results_repeated_{bm}.csv").sort_values(by=["fuzzer_combination"],
                                                                                           ascending=[False])
    # df['max_increment'] = df["max"].diff().abs()
    # df['avg_increment'] = df["avg"].diff().abs()
    df['max_increment'] = df['max'] / df['max'].shift(1)
    df['max_increment'] = df['max_increment'].apply(lambda x: round(x, 4)).fillna(1.00)
    # df['avg_increment']=(df['avg']-df['avg'].shift(1))/df['avg'].shift(1)
    df['avg_increment'] = df['avg'] / df['avg'].shift(1)
    df['avg_increment'] = df['avg_increment'].apply(lambda x: round(x, 4)).fillna(1.00)
    print(df)
    dfs.append(df)
df_edge_count_global_all = pd.concat(dfs, ignore_index=True).sort_values(by=["benchmark", "fuzzer_combination"],
                                                                         ascending=[True, False]).reset_index(drop=True)
# cols_to_keep = ["benchmark","fuzzer_combination","experiment_id","edge_count"]
# df_edge_count_global_all.drop(df_edge_count_global_all.columns.difference(cols_to_keep), axis=1, inplace=True)
df_edge_count_global_all.drop(["Unnamed: 0"], axis=1, inplace=True)
print(df_edge_count_global_all)

df_edge_count_global_all.to_csv(f"csv/fscve_step6_metric1_edge_coverage_global_all.csv")

df_edge_count_global_all_transfer = df_edge_count_global_all.T
print(df_edge_count_global_all_transfer)
df_edge_count_global_all_transfer.to_csv(f"csv/fscve_step6_metric1_edge_coverage_global_all_transfer.csv")

# # calc the total number of unique edges
# # edge coverage global detail of one fuzzer combinations
# dfs_totalunique = []
# for bm in benchmarks:
#     df_totalunique = pd.read_csv(f"csv/fscve_edge_detail_{bm}.csv").sort_values(by=["benchmark", "fuzzer_combination"],
#                                                                                 ascending=[True, False])
#     df_totalunique["total_unique"] = df_totalunique["edge"]
#     df_totalunique = df_totalunique.groupby(["benchmark", "fuzzer_combination"])[["total_unique"]].count().reset_index(
#         drop=False)
#     # print(df)
#     dfs_totalunique.append(df_totalunique)
# df_edge_total_unique_all = pd.concat(dfs_totalunique, ignore_index=True).sort_values(
#     by=["benchmark", "fuzzer_combination"], ascending=[True, False]).reset_index(drop=True)
# print(df_edge_total_unique_all)
# df_edge_total_unique_all.to_csv(f"csv/fscve_step6_metric1_totalunique_all.csv")

# df_edge_total_unique.to_csv(f"csv/fscve_step6_metric1_totalunique_{benchmark}_{fc}_all.csv")
print("+++" * 20)
# calc the total unique edges of a fc on special benchmark
# for enfuzz,the old data collected didn't include edge-coverage-fuzzer db table
# so,it needs to obtain the info from edge-coverage-global,instead of fscve_edge_detail_{benchmark}_{fc}_{expid}.csv
dfs_total_unique = []
for bm in benchmarks:
    for fc in fcs:
        df = pd.read_csv(f"csv/fscve_step6_metric1_totalunique_{bm}_{fc}_all.csv")
        dfs_total_unique.append(df)
df_total_unique_final = pd.concat(dfs_total_unique, ignore_index=True).sort_values(
    by=["benchmark", "fuzzer_combination"], ascending=[True, False]).reset_index(drop=True)
df_total_unique_final.drop(["Unnamed: 0"], axis=1, inplace=True)
#calc how many times needed to achieve the total unique edges on average
df_total_unique_final["times"]=df_total_unique_final["total_unique"]/df_edge_count_global_all["avg"]
print(df_total_unique_final)
df_total_unique_final.to_csv(f"csv/fscve_step6_metric1_totalunique_all.csv")


