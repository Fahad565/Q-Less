"use client";

import React, { useState, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Service {
  id: number;
  name: string;
  code_prefix: string;
  avg_service_minutes: number;
}

interface Counter {
  id: number;
  name: string;
  is_active: boolean;
}

interface Ticket {
  id: number;
  ticket_number: string;
  customer_phone: string;
  queue_id: number;
  service_id: number;
  counter_id: number | null;
  status: string;
  created_at: string;
  called_at: string | null;
  completed_at: string | null;
  position: number | null;
  estimated_wait_minutes: number | null;
  service_name: string | null;
  counter_name: string | null;
}

interface QueueData {
  id: number;
  name: string;
  location: string;
  services: Service[];
  counters: Counter[];
  tickets: Ticket[];
}

interface SMSLog {
  id: string;
  phone_number: string;
  message: string;
  type: string;
  timestamp: string;
}

export default function Dashboard() {
  const [queue, setQueue] = useState<QueueData | null>(null);
  const [smsLogs, setSmsLogs] = useState<SMSLog[]>([]);
  const [selectedCounter, setSelectedCounter] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // USSD Simulator State
  const [ussdPhone, setUssdPhone] = useState<string>("+254712345678");
  const [ussdInput, setUssdInput] = useState<string>("");
  const [ussdScreen, setUssdScreen] = useState<string>("");
  const [ussdSessionActive, setUssdSessionActive] = useState<boolean>(false);

  const fetchQueueData = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/queues/1`);
      if (!res.ok) throw new Error("Failed to fetch queue data");
      const data = await res.json();
      setQueue(data);
      if (data.counters && data.counters.length > 0 && !selectedCounter) {
        setSelectedCounter(data.counters[0].id);
      }
      setError(null);
    } catch (err: any) {
      setError("Error connecting to backend API");
    } finally {
      setLoading(false);
    }
  };

  const fetchSMSLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/notifications/logs`);
      if (res.ok) {
        const logs = await res.json();
        setSmsLogs(logs.reverse());
      }
    } catch (e) {
      console.error("Error fetching SMS logs", e);
    }
  };

  useEffect(() => {
    fetchQueueData();
    fetchSMSLogs();
    const interval = setInterval(() => {
      fetchQueueData();
      fetchSMSLogs();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleCallNext = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/queues/1/call-next?counter_id=${selectedCounter}`, {
        method: "POST"
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || "Failed to call next ticket");
        return;
      }
      await fetchQueueData();
      await fetchSMSLogs();
    } catch (e) {
      alert("Error calling next ticket");
    }
  };

  const handleAction = async (ticketId: number, action: "complete" | "skip" | "recall" | "cancel") => {
    try {
      const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/${action}`, {
        method: "POST"
      });
      if (!res.ok) {
        const errData = await res.json();
        alert(errData.detail || `Failed to ${action} ticket`);
        return;
      }
      await fetchQueueData();
      await fetchSMSLogs();
    } catch (e) {
      alert(`Error executing ${action}`);
    }
  };

  const handleAssignCounter = async (ticketId: number, counterId: number) => {
    try {
      const res = await fetch(`${API_BASE}/api/tickets/${ticketId}/assign-counter`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ counter_id: counterId })
      });
      if (!res.ok) throw new Error("Failed to assign counter");
      await fetchQueueData();
      await fetchSMSLogs();
    } catch (e) {
      alert("Error assigning counter");
    }
  };

  // USSD Simulation Handlers
  const sendUssdRequest = async (textVal: string) => {
    try {
      const params = new URLSearchParams();
      params.append("sessionId", "dash_session_123");
      params.append("serviceCode", "*384#");
      params.append("phoneNumber", ussdPhone);
      params.append("text", textVal);

      const res = await fetch(`${API_BASE}/api/ussd`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: params.toString()
      });

      const responseText = await res.text();
      setUssdScreen(responseText);
      if (responseText.startsWith("END")) {
        setUssdSessionActive(false);
      } else {
        setUssdSessionActive(true);
      }
      fetchQueueData();
      fetchSMSLogs();
    } catch (e) {
      setUssdScreen("END Network error calling USSD service.");
      setUssdSessionActive(false);
    }
  };

  const startUssdSession = () => {
    setUssdInput("");
    sendUssdRequest("");
  };

  const submitUssdInput = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ussdInput.trim()) return;
    const newInput = ussdInput;
    setUssdInput("");
    sendUssdRequest(newInput);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-white flex items-center justify-center">
        <div className="text-xl font-semibold animate-pulse">Loading Q-Less Dashboard...</div>
      </div>
    );
  }

  const activeTickets = queue?.tickets || [];
  const servingTickets = activeTickets.filter((t) => t.status === "CALLED" || t.status === "SERVING");
  const waitingTickets = activeTickets.filter((t) => t.status === "WAITING");

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* HEADER */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="bg-emerald-500 text-slate-950 font-bold p-2 rounded-lg text-xl tracking-wider">
            Q-LESS
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">{queue?.name || "Mombasa Service Centre"}</h1>
            <p className="text-xs text-slate-400">Virtual Queue Management & Customer Support</p>
          </div>
        </div>

        <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-lg border border-slate-700">
          <label className="text-sm font-medium text-slate-300">Active Counter:</label>
          <select
            value={selectedCounter}
            onChange={(e) => setSelectedCounter(Number(e.target.value))}
            className="bg-slate-800 border border-slate-600 rounded px-3 py-1 text-sm font-semibold text-emerald-400 focus:outline-none focus:border-emerald-500"
          >
            {queue?.counters.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>

          <button
            onClick={handleCallNext}
            disabled={waitingTickets.length === 0}
            className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white font-bold px-5 py-2 rounded-lg shadow-lg transition-all text-sm flex items-center gap-2"
          >
            📢 Call Next
          </button>
        </div>
      </header>

      {/* ERROR ALERT */}
      {error && (
        <div className="bg-rose-900/80 border border-rose-600 text-rose-200 px-6 py-3 text-sm flex justify-between items-center">
          <span>{error}</span>
          <button onClick={fetchQueueData} className="underline hover:text-white">Retry</button>
        </div>
      )}

      {/* MAIN CONTENT GRID */}
      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* LEFT & CENTER SURFACES: QUEUE MANAGEMENT */}
        <div className="lg:col-span-8 flex flex-col gap-6">

          {/* NOW SERVING SECTION */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
            <h2 className="text-sm font-bold tracking-wider text-emerald-400 uppercase mb-4 flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
              Now Serving
            </h2>

            {servingTickets.length === 0 ? (
              <div className="border border-dashed border-slate-700 rounded-lg p-8 text-center text-slate-500">
                No tickets currently being served. Click <span className="text-emerald-400 font-semibold">Call Next</span> to start serving.
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {servingTickets.map((t) => (
                  <div key={t.id} className="bg-slate-900 border border-emerald-500/40 rounded-xl p-5 flex flex-col justify-between shadow-lg">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="text-3xl font-extrabold text-emerald-400 tracking-tight">{t.ticket_number}</div>
                        <div className="text-xs text-slate-400 font-mono mt-1">{t.customer_phone}</div>
                      </div>
                      <span className="bg-emerald-950 text-emerald-300 border border-emerald-700 text-xs px-3 py-1 rounded-full font-bold">
                        {t.counter_name || "Unassigned Counter"}
                      </span>
                    </div>

                    <div className="text-sm text-slate-300 mb-4">
                      Service: <span className="font-semibold text-white">{t.service_name}</span>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-slate-800">
                      <button
                        onClick={() => handleAction(t.id, "complete")}
                        className="flex-1 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-1.5 px-3 rounded text-xs transition"
                      >
                        ✓ Complete
                      </button>
                      <button
                        onClick={() => handleAction(t.id, "recall")}
                        className="bg-amber-600 hover:bg-amber-500 text-white font-semibold py-1.5 px-3 rounded text-xs transition"
                      >
                        🔁 Recall
                      </button>
                      <button
                        onClick={() => handleAction(t.id, "skip")}
                        className="bg-slate-700 hover:bg-slate-600 text-slate-200 font-semibold py-1.5 px-3 rounded text-xs transition"
                      >
                        ⏭ Skip
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* WAITING QUEUE SECTION */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl flex-1">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold tracking-wider text-slate-300 uppercase flex items-center gap-2">
                👥 Waiting Queue <span className="bg-slate-700 text-slate-200 text-xs px-2.5 py-0.5 rounded-full">{waitingTickets.length}</span>
              </h2>
            </div>

            {waitingTickets.length === 0 ? (
              <div className="border border-dashed border-slate-700 rounded-lg p-8 text-center text-slate-500">
                The waiting queue is empty.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="border-b border-slate-700 text-slate-400 text-xs uppercase font-semibold">
                      <th className="py-3 px-4">Pos</th>
                      <th className="py-3 px-4">Ticket</th>
                      <th className="py-3 px-4">Phone</th>
                      <th className="py-3 px-4">Service</th>
                      <th className="py-3 px-4">Est. Wait</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50 text-sm">
                    {waitingTickets.map((t) => (
                      <tr key={t.id} className="hover:bg-slate-750/50 transition">
                        <td className="py-3 px-4 font-bold text-emerald-400">#{t.position}</td>
                        <td className="py-3 px-4 font-mono font-bold text-white">{t.ticket_number}</td>
                        <td className="py-3 px-4 font-mono text-slate-400 text-xs">{t.customer_phone}</td>
                        <td className="py-3 px-4 text-slate-300">{t.service_name}</td>
                        <td className="py-3 px-4 text-slate-400 text-xs">~{t.estimated_wait_minutes} mins</td>
                        <td className="py-3 px-4 text-right space-x-2">
                          <button
                            onClick={() => handleAction(t.id, "cancel")}
                            className="text-rose-400 hover:text-rose-300 text-xs font-semibold px-2 py-1 rounded hover:bg-rose-950 transition"
                          >
                            Cancel
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT SURFACE: USSD SIMULATOR & SMS NOTIFICATION LOGS */}
        <div className="lg:col-span-4 flex flex-col gap-6">

          {/* USSD SIMULATOR DRAWER */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-xl">
            <h2 className="text-sm font-bold tracking-wider text-sky-400 uppercase mb-3 flex items-center gap-2">
              📱 USSD Phone Simulator
            </h2>
            <p className="text-xs text-slate-400 mb-4">
              Simulate Africa's Talking USSD requests directly in your browser to test queue joining and checking.
            </p>

            <div className="bg-slate-950 border border-slate-700 rounded-lg p-4 mb-4 font-mono text-sm">
              <div className="text-xs text-slate-500 mb-2 border-b border-slate-800 pb-1 flex justify-between">
                <span>SIMULATOR SCREEN</span>
                <span>*384#</span>
              </div>

              <div className="min-h-[120px] whitespace-pre-wrap text-emerald-400">
                {ussdScreen || "Click 'Dial *384#' to begin a USSD session."}
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={ussdPhone}
                  onChange={(e) => setUssdPhone(e.target.value)}
                  placeholder="Phone number"
                  className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-xs font-mono flex-1 focus:outline-none focus:border-sky-500"
                />
                <button
                  onClick={startUssdSession}
                  className="bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold px-3 py-1.5 rounded transition"
                >
                  Dial *384#
                </button>
              </div>

              {ussdSessionActive && (
                <form onSubmit={submitUssdInput} className="flex gap-2">
                  <input
                    type="text"
                    value={ussdInput}
                    onChange={(e) => setUssdInput(e.target.value)}
                    placeholder="Enter menu choice..."
                    className="bg-slate-900 border border-slate-700 text-white rounded px-3 py-1.5 text-xs font-mono flex-1 focus:outline-none focus:border-emerald-500"
                  />
                  <button
                    type="submit"
                    className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-3 py-1.5 rounded transition"
                  >
                    Send
                  </button>
                </form>
              )}
            </div>
          </div>

          {/* MOCK SMS NOTIFICATION LOGS */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-xl flex-1 flex flex-col">
            <div className="flex justify-between items-center mb-3">
              <h2 className="text-sm font-bold tracking-wider text-amber-400 uppercase flex items-center gap-2">
                📩 Live SMS Feed
              </h2>
              <span className="text-xs text-slate-500 font-mono">Mock Provider</span>
            </div>

            <div className="bg-slate-950 border border-slate-700 rounded-lg p-3 flex-1 overflow-y-auto max-h-[350px] space-y-3 font-mono text-xs">
              {smsLogs.length === 0 ? (
                <div className="text-slate-600 text-center py-6">No SMS notifications sent yet.</div>
              ) : (
                smsLogs.map((log) => (
                  <div key={log.id} className="bg-slate-900 border border-slate-800 rounded p-2.5 space-y-1">
                    <div className="flex justify-between items-center text-[10px] text-slate-400 border-b border-slate-800/80 pb-1">
                      <span className="text-amber-400 font-semibold">{log.phone_number}</span>
                      <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                    </div>
                    <div className="text-slate-200 leading-snug pt-1">{log.message}</div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
}
