#include <bits/stdc++.h>
using namespace std;

tuple<int, string, string> LocalAlignment(int match, int mismatch, int penalty, string s, string t)
{
    // Initialization
    int n = s.size(), m = t.size(), maxX = 1, maxY = 1;

    // Finding the best match with iterative DP
    vector<vector<int>> dp(n + 1, vector<int>(m + 1, 0));
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
        {
            // Checking if there is a match/mismatch in our current position and updating our max
            dp[i + 1][j + 1] = max(dp[i][j] + (s[i] == t[j] ? match : -mismatch), dp[i + 1][j + 1]);

            // Storing the max from all previous cases minus a penalty for an indel
            dp[i + 1][j + 1] = max(dp[i][j + 1] - penalty, dp[i + 1][j + 1]);
            dp[i + 1][j + 1] = max(dp[i + 1][j] - penalty, dp[i + 1][j + 1]);

            // Zero case for Local alignment
            dp[i + 1][j + 1] = max(dp[i + 1][j + 1], 0);

            // Keeping track of the position of the Max Local Alignment
            if (dp[i + 1][j + 1] > dp[maxX][maxY])
                maxX = i + 1, maxY = j + 1;
        }

    // Doing the Buildback
    int i = maxX, j = maxY, maxAlignment = dp[maxX][maxY];
    string ans1 = "", ans2 = "";

    // While are not at a 0 in our DP, we add another letter to our alignments
    while (dp[i][j] > 0)
    {
        // Letters matched here in the max alignment
        if (i > 0 && j > 0 && dp[i][j] == dp[i - 1][j - 1] + match)
            ans1.push_back(s[--i]), ans2.push_back(t[--j]);

        // mismatch case
        else if (i > 0 && j > 0 && dp[i][j] == dp[i - 1][j - 1] - mismatch)
            ans1.push_back(s[--i]), ans2.push_back(t[--j]);

        // Adding indels for the respective strings
        else if (i > 0 && dp[i][j] == dp[i - 1][j] - penalty)
            ans1.push_back(s[--i]), ans2.push_back('-');

        else
            ans1.push_back('-'), ans2.push_back(t[--j]);
    }

    // Reversing since the buildback was done in reverese
    reverse(ans1.begin(), ans1.end());
    reverse(ans2.begin(), ans2.end());
    return {maxAlignment, ans1, ans2};
}