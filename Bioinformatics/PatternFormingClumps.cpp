#include <bits/stdc++.h>
using namespace std;
#define rep(i, a, b) for (ll i = a; i < (ll)b; ++i)
typedef long long ll;

vector <string> FindClumps(string Genome, int k, int L, int t)
{
    unordered_set<string> ans;
    unordered_map<string, ll> mp;

    // Sliding window for L
    rep (i, 0, Genome.size()-k+1)
    {
        // updating which substrings we are seeing based on our window
        if (i+k-1 >= L) mp[Genome.substr(i-L+k-1, k)]--;
        mp[Genome.substr(i, k)]++;

        // Inserting the front most k-mer found if possible
        if (mp[Genome.substr(i, k)] >= t)
            ans.insert(Genome.substr(i, k));
    }

    vector<string> res;
    for (auto x : ans) res.push_back(x);

    return res;
}