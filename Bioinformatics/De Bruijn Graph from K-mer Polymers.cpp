#include <bits/stdc++.h>
using namespace std;
using k_mer_edgelist_t = unordered_map<string, vector<string>>;


k_mer_edgelist_t DeBruijnKmers(vector<string> k_mers)
{
    unordered_map<string, vector<string>> adj;
    for (string k : k_mers)
        adj[k.substr(0, k.size() - 1)].push_back(k.substr(1));

    return adj;
}