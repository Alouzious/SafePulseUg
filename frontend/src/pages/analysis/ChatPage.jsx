import { useState, useEffect, useRef } from 'react';
import toast                           from 'react-hot-toast';
import { MessageSquareText, Send, RotateCcw, Bot, User, Zap, ChevronRight } from 'lucide-react';
import analysisApi                     from '../../api/analysisApi';

const ChatPage = () => {
    const [messages,  setMessages]  = useState([]);
    const [input,     setInput]     = useState('');
    const [loading,   setLoading]   = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const bottomRef                 = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const sendMessage = async () => {
        const text = input.trim();
        if (!text || loading) return;

        const userMsg = { role: 'user', content: text, id: Date.now() };
        setMessages((prev) => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await analysisApi.chat(text, sessionId);
            if (!sessionId) setSessionId(res.data.session_id);
            setMessages((prev) => [...prev, {
                role: 'assistant', content: res.data.response, id: Date.now() + 1,
            }]);
        } catch {
            toast.error('Agent failed to respond. Check your Gemini API key.');
            setMessages((prev) => prev.filter((m) => m.id !== userMsg.id));
        } finally {
            setLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    };

    const startNewChat = () => {
        setMessages([]); setSessionId(null); setInput('');
    };

    const QUICK_PROMPTS = [
        'What are the most common crimes this month?',
        'Which districts have the most unsolved cases?',
        'Show me all robbery cases',
        'What patterns do you see in recent crimes?',
        'List all high severity unsolved cases',
        'Analyze crime trends in Kampala',
    ];

    return (
        <div className="flex flex-col h-[calc(100vh-90px)]">

            {/* ── Header ───────────────────────────────── */}
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h1 className="text-2xl font-bold text-[#0f2744] flex items-center gap-2">
                        <MessageSquareText size={24} className="text-blue-600" />
                        AI Agent Chat
                    </h1>
                    <p className="text-slate-500 text-sm mt-0.5">
                        Chat with SafePulse AI — Ask anything about crime data
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    {sessionId && (
                        <span className="text-xs text-slate-400 bg-slate-100 px-3 py-1 rounded-full flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                            Session active
                        </span>
                    )}
                    <button
                        onClick={startNewChat}
                        className="flex items-center gap-2 px-4 py-2 border border-slate-200 rounded-lg text-sm font-semibold text-[#0f2744] hover:bg-slate-50 transition"
                    >
                        <RotateCcw size={14} />
                        New Chat
                    </button>
                </div>
            </div>

            <div className="flex flex-1 gap-4 overflow-hidden">

                {/* ── Quick Prompts Sidebar ─────────────── */}
                <div className="w-52 flex-shrink-0">
                    <div className="bg-white rounded-2xl p-4 border border-slate-100 shadow-sm h-full">
                        <div className="flex items-center gap-2 mb-3">
                            <Zap size={14} className="text-[#0f2744]" />
                            <p className="text-sm font-bold text-[#0f2744]">Quick Questions</p>
                        </div>
                        <div className="space-y-1.5">
                            {QUICK_PROMPTS.map((p) => (
                                <button
                                    key={p}
                                    onClick={() => setInput(p)}
                                    className="w-full flex items-start gap-2 px-2.5 py-2 bg-slate-50 hover:bg-blue-50 hover:border-blue-200 border border-slate-100 rounded-lg text-[11px] text-slate-700 text-left leading-relaxed transition group"
                                >
                                    <ChevronRight size={10} className="mt-0.5 flex-shrink-0 text-slate-300 group-hover:text-blue-400" />
                                    {p}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* ── Chat Window ───────────────────────── */}
                <div className="flex-1 flex flex-col bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-5 space-y-4">

                        {/* Welcome state */}
                        {messages.length === 0 && (
                            <div className="flex flex-col items-center justify-center h-full gap-3 text-slate-400">
                                <div className="w-16 h-16 rounded-2xl bg-[#0f2744] flex items-center justify-center shadow-lg">
                                    <Bot size={32} className="text-blue-400" />
                                </div>
                                <p className="text-lg font-semibold text-slate-600">SafePulse AI Agent</p>
                                <p className="text-sm text-center max-w-sm text-slate-400 leading-relaxed">
                                    I can analyze crime data, identify patterns, find hotspots, and answer questions about cases in the database. Ask me anything!
                                </p>
                            </div>
                        )}

                        {/* Messages */}
                        {messages.map((msg) => (
                            <div
                                key={msg.id}
                                className={`flex items-end gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                            >
                                {/* Avatar */}
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm
                                    ${msg.role === 'assistant' ? 'bg-[#0f2744]' : 'bg-blue-600'}`}>
                                    {msg.role === 'assistant'
                                        ? <Bot size={16} className="text-blue-300" />
                                        : <User size={16} className="text-white" />
                                    }
                                </div>

                                {/* Bubble */}
                                <div className={`max-w-[75%] px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap shadow-sm
                                    ${msg.role === 'user'
                                        ? 'bg-[#0f2744] text-white rounded-2xl rounded-br-sm'
                                        : 'bg-slate-50 text-slate-700 rounded-2xl rounded-bl-sm border border-slate-100'
                                    }`}>
                                    {msg.content}
                                </div>
                            </div>
                        ))}

                        {/* Typing indicator */}
                        {loading && (
                            <div className="flex items-end gap-2.5">
                                <div className="w-8 h-8 rounded-full bg-[#0f2744] flex items-center justify-center flex-shrink-0">
                                    <Bot size={16} className="text-blue-300" />
                                </div>
                                <div className="px-4 py-3 bg-slate-50 rounded-2xl rounded-bl-sm border border-slate-100 flex items-center gap-1">
                                    {[0, 1, 2].map((i) => (
                                        <div
                                            key={i}
                                            className="w-2 h-2 rounded-full bg-slate-400 animate-bounce"
                                            style={{ animationDelay: `${i * 0.15}s` }}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}

                        <div ref={bottomRef} />
                    </div>

                    {/* ── Input Bar ─────────────────────── */}
                    <div className="px-4 py-3 border-t border-slate-100 flex gap-3 items-end">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask the AI agent about crime data... (Enter to send, Shift+Enter for new line)"
                            rows={2}
                            className="flex-1 px-4 py-2.5 border border-slate-200 rounded-xl text-sm resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 transition leading-relaxed"
                        />
                        <button
                            onClick={sendMessage}
                            disabled={loading || !input.trim()}
                            className="h-11 px-5 bg-[#0f2744] hover:bg-[#1a3a5c] text-white rounded-xl font-semibold text-sm flex items-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed transition"
                        >
                            <Send size={15} />
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatPage;