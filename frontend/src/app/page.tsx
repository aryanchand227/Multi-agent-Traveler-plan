import Link from "next/link";

export default function HomePage() {
  return (
    <div className="min-h-[calc(100vh-8rem)] bg-gradient-to-b from-blue-50/50 via-white to-slate-50 py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 text-blue-800 text-xs font-semibold mb-6">
          <span>🤖</span> Powered by Multi-Agent LangGraph Architecture
        </div>

        {/* Hero Title */}
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-gray-900 mb-6">
          Intelligent Multi-Agent <br />
          <span className="text-blue-600">Travel Planning Platform</span>
        </h1>

        <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto mb-10 leading-relaxed">
          Not just a simple chatbot — a production-grade multi-agent system.
          Specialized agents collaborate to compare transportation, find optimal stays,
          forecast destination weather, and balance your budget in real time.
        </p>

        {/* Primary Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link
            href="/plan"
            className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl bg-blue-600 px-8 py-3.5 text-base font-semibold text-white shadow-lg shadow-blue-500/30 hover:bg-blue-700 transition"
          >
            Start Planning Trip →
          </Link>
          <Link
            href="/preferences"
            className="w-full sm:w-auto inline-flex items-center justify-center rounded-xl border border-gray-300 bg-white px-8 py-3.5 text-base font-semibold text-gray-700 hover:bg-gray-50 transition shadow-sm"
          >
            ⚙ Configure Travel Preferences
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-sm hover:shadow-md transition">
            <div className="h-10 w-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center text-xl mb-4">
              🚆
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-1">
              Multi-Modal Transport Comparison
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Bus, Train, and Flight subagents evaluate travel times, costs, comfort tiers,
              and availability, ranking choices with clear decision factors.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-sm hover:shadow-md transition">
            <div className="h-10 w-10 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center text-xl mb-4">
              🏨
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-1">
              Accommodation & Activities
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Finds verified accommodations matching your style (hostel, 3-star, boutique, or luxury)
              and curates personalized sightseeing itineraries.
            </p>
          </div>

          <div className="bg-white p-6 rounded-2xl border border-gray-200/80 shadow-sm hover:shadow-md transition">
            <div className="h-10 w-10 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center text-xl mb-4">
              ⚡
            </div>
            <h3 className="font-bold text-gray-900 text-lg mb-1">
              Real-Time SSE & Replanning
            </h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Watch agents deliberate via live Server-Sent Events. Modify your plan on the fly
              with stateful partial replanning.
            </p>
          </div>
        </div>

        {/* Sample Prompts */}
        <div className="mt-14 p-6 bg-slate-50 border border-slate-200 rounded-2xl text-center">
          <p className="text-xs uppercase font-bold text-slate-500 tracking-wider mb-3">
            Popular Example Requests
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {[
              "4-day trip from Bangalore to Goa for 2 people with ₹25,000 budget",
              "Weekend getaway to Ooty by train under ₹15,000",
              "Luxury 5-day holiday in Jaipur with cultural sightseeing",
            ].map((example, i) => (
              <Link
                key={i}
                href={`/plan`}
                className="text-xs bg-white border border-slate-200 text-slate-700 px-3 py-1.5 rounded-full hover:border-blue-500 hover:text-blue-600 transition"
              >
                "{example}"
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
