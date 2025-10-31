#include <bits/stdc++.h>
using namespace std;
#define all(x) (x).begin(), (x).end()
#define sz(x) (int)(x).size()
#define rep(i, a, b) for (int i = a; i < (int)b; ++i)
typedef long double ld;


vector<string> GibbsSampler(vector<string> DNA, int k, int t, int N)
{
    // Setting up a random number generator
    random_device rd;
    mt19937 gen(rd());

    // The program had difficulty finding the global minimum under a small N
    N = 100000;

    // Initialization
    map<char, int> mp = {{'A', 0}, {'C', 1}, {'G', 2}, {'T', 3}};
    vector<int> motifs(t), bestMotifs;
    int bestScore = 100000;

    // Adding our initial motifs
    rep (i, 0, t)
    {
        uniform_int_distribution<> dist(0, sz(DNA[i])-k);
        motifs[i] = dist(gen);
    }

    bestMotifs = motifs;

    // The iterative process to find better motifs
    rep (x, 0, N)
    {
        // Randomly picking a removal index
        uniform_int_distribution<> dist(0, t-1);
        int removalIndex = dist(gen);

        // Creating a profile based on the motifs - not including motif 'removalIndex'
        vector<vector<ld>> profile(4, vector<ld>(k, 0.0));

        rep (i, 0, t) if (i != removalIndex)
            rep (j, 0, k) profile[mp[DNA[i][j+motifs[i]]]][j]++;

        // Adding pseudocounts
        rep (i, 0, 4) rep (j, 0, k)
            profile[i][j] += 1.0;

        // Finding the probabilities for each k-mer in the removed string
        vector<ld> prob;
        rep (start, 0, sz(DNA[removalIndex]) - k + 1)
        {
            ld p = 1.0;
            rep (j, 0, k) p *= profile[mp[DNA[removalIndex][start + j]]][j];
            prob.push_back(p);
        }

        // Picking a random motif based on the probabilities we calculated
        discrete_distribution<> newMotifDist(all(prob));
        motifs[removalIndex] = newMotifDist(gen);

        // Finding the score for the new set of motifs
        int currentScore = 0;
        rep (j, 0, k)
        {
            vector<int> colCount(4, 0);
            rep (i, 0, t) colCount[mp[DNA[i][motifs[i] + j]]]++;
            currentScore += t - *max_element(all(colCount));
        }

        // Updating bestMotifs if we improved score
        if (currentScore < bestScore)
        {
            bestScore = currentScore;
            bestMotifs = motifs;
        }
    }

    vector<string> ans;
    rep (i, 0, t)
        ans.push_back(DNA[i].substr(bestMotifs[i], k));

    return ans;
}