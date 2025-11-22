import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

interface LeaderboardEntry {
  user_id: string;
  pnl: number;
}

function LeaderboardWidget() {
  const { token } = useAuth();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);

  const competitionId = 1;

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };

        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const response = await fetch(
          `${API_BASE_URL}/leaderboard/competitions/${competitionId}/leaderboard`,
          {
            method: "GET",
            headers,
          }
        );

        if (!response.ok) {
          throw new Error(`Failed to fetch leaderboard: ${response.statusText}`);
        }

        const data: LeaderboardEntry[] = await response.json();
        setLeaderboard(data);
      } catch (err) {
        console.error("Error fetching leaderboard:", err);
      }
    };

    fetchLeaderboard();
  }, [competitionId, token]);

  const formatPnl = (pnl: number): string => {
    const sign = pnl >= 0 ? "+" : "";
    return `${sign}${pnl.toFixed(2)}`;
  };

  const ourTeam = leaderboard.find((entry) => {
    // TODO: 실제 사용자 ID와 비교하도록 수정 필요
    return entry.user_id === "user123";
  });
  const ourTeamRank = ourTeam ? leaderboard.indexOf(ourTeam) + 1 : null;

  return (
    <div className="flex flex-col gap-3 text-sm">
      <div>
        <div className="grid grid-cols-[40px_1fr_70px] px-2 py-1.5 text-xs font-semibold text-gray-600 border-b border-gray-200 bg-gray-50">
          <span>Rank</span>
          <span>Team</span>
          <span className="text-right">PnL</span>
        </div>
        <div className="max-h-[200px] overflow-y-auto border border-t-0 border-gray-200">
          {leaderboard.map((entry, index) => {
            const rank = index + 1;
            return (
              <div
                key={entry.user_id}
                className="grid grid-cols-[40px_1fr_70px] px-2 py-1.5 border-b border-gray-100 items-center"
              >
                <span className="font-semibold">{rank}</span>
                <span>{entry.user_id}</span>
                <span
                  className={`text-right font-medium ${
                    entry.pnl >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {formatPnl(entry.pnl)}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {ourTeam && ourTeamRank && (
        <div className="p-2.5 bg-emerald-50 border border-emerald-300 rounded-md text-xs">
          <div className="mb-1.5 text-emerald-800 font-semibold">Our Team</div>
          <div className="flex justify-between items-center">
            <div>
              <div className="text-xl font-extrabold text-emerald-900">#{ourTeamRank}</div>
              <div className="mt-1 font-semibold">{ourTeam.user_id}</div>
            </div>
            <div
              className={`text-base font-bold ${
                ourTeam.pnl >= 0 ? "text-emerald-800" : "text-red-600"
              }`}
            >
              {formatPnl(ourTeam.pnl)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LeaderboardWidget;


