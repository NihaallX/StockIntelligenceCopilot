import TodaysWatchDashboard from "@/components/todays-watch-dashboard"

export default function IntradayPage() {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Intraday Monitor</h1>
        <p className="text-gray-600">
          Deterministic detection of weakness, extended moves, and portfolio risks
        </p>
      </div>
      
      <TodaysWatchDashboard />
    </div>
  )
}
