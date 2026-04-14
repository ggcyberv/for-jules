import { useState, useEffect } from 'react';
import { Search, Library, ScrollText, BarChart3, Plus, Eye, Type as TypeIcon, ChevronRight, Filter, Minus, Tag as TagIcon, X } from 'lucide-react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const API_BASE = 'http://localhost:8000';

interface CardDetails {
  image_uris?: { normal: string };
  oracle_text?: string;
  prices?: { eur: string };
  type_line?: string;
  mana_cost?: string;
  color_identity?: string[];
  cmc?: number;
  legalities?: Record<string, string>;
  keywords?: string[];
}

interface CollectionItem {
  oracle_id: string;
  name: string;
  quantity: number;
  details: CardDetails;
  decks: string[];
  tags: string[];
}

interface Deck {
  id: number;
  name: string;
  description?: string;
}

interface DeckDetailCard {
  oracle_id: string;
  name: string;
  quantity: number;
  category: string;
  details: CardDetails;
}

interface DeckDetails extends Deck {
  cards: DeckDetailCard[];
}

interface ValueHistoryEntry {
  timestamp: string;
  value: number;
}

interface Stats {
  total_value: number;
  history: ValueHistoryEntry[];
}

const App = () => {
  const [activeTab, setActiveTab] = useState('collection');
  const [collection, setCollection] = useState<CollectionItem[]>([]);
  const [decks, setDecks] = useState<Deck[]>([]);
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null);
  const [stats, setStats] = useState<Stats>({ total_value: 0, history: [] });

  useEffect(() => {
    fetchCollection();
    fetchDecks();
    fetchStats();
  }, []);

  const fetchCollection = async (params = {}) => {
    try {
      const res = await axios.get(`${API_BASE}/collection`, { params });
      setCollection(res.data);
    } catch (e) { console.error(e); }
  };

  const fetchDecks = async () => {
    try {
      const res = await axios.get(`${API_BASE}/decks`);
      setDecks(res.data);
    } catch (e) { console.error(e); }
  };

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_BASE}/stats/value`);
      setStats(res.data);
    } catch (e) { console.error(e); }
  };

  return (
    <div className="flex h-screen bg-slate-900 text-slate-100 font-sans overflow-hidden">
      <div className="w-64 bg-slate-800 border-r border-slate-700 flex flex-col shrink-0">
        <div className="p-6 text-2xl font-bold text-indigo-400 flex items-center gap-2">
          <Library size={32} />
          <span>MTG Hub</span>
        </div>
        <nav className="flex-1 px-4 space-y-2">
          <button onClick={() => setActiveTab('collection')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'collection' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-700 text-slate-400'}`}><Library size={20} />Collection</button>
          <button onClick={() => setActiveTab('decks')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'decks' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-700 text-slate-400'}`}><ScrollText size={20} />Decks</button>
          <button onClick={() => setActiveTab('stats')} className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${activeTab === 'stats' ? 'bg-indigo-600 text-white' : 'hover:bg-slate-700 text-slate-400'}`}><BarChart3 size={20} />Statistics</button>
        </nav>
        <div className="p-4 border-t border-slate-700">
          <div className="text-xs text-slate-500 uppercase font-semibold mb-2">Collection Value</div>
          <div className="text-xl font-bold text-emerald-400">€{stats.total_value.toFixed(2)}</div>
        </div>
      </div>
      <div className="flex-1 overflow-auto bg-slate-900">
        {activeTab === 'collection' && <CollectionView collection={collection} refresh={fetchCollection} decks={decks} />}
        {activeTab === 'decks' && <DecksView decks={decks} selectedDeck={selectedDeck} setSelectedDeck={setSelectedDeck} refresh={fetchDecks} />}
        {activeTab === 'stats' && <StatsView stats={stats} />}
      </div>
    </div>
  );
};

const CollectionView = ({ collection, refresh, decks }: { collection: CollectionItem[], refresh: (p?: any) => void, decks: Deck[] }) => {
  const [search, setSearch] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [displayMode, setDisplayMode] = useState<'image' | 'text'>('image');
  const [filters, setFilters] = useState({ colors: [] as string[], colorIdentity: [] as string[], format: '', type: '', keyword: '', set_code: '', tag: '' });
  const [newTag, setNewTag] = useState<{ [key: string]: string }>({});
  const [deckAction, setDeckAction] = useState<{ [key: string]: { deckId: number, category: string } }>({});
  const [availableTags, setAvailableTags] = useState<string[]>([]);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    const res = await axios.get(`${API_BASE}/tags`);
    setAvailableTags(res.data);
  };

  const handleColorToggle = (color: string) => {
    const newColors = filters.colors.includes(color)
      ? filters.colors.filter(c => c !== color)
      : [...filters.colors, color];
    setFilters({ ...filters, colors: newColors });
  };

  const handleIdentityToggle = (color: string) => {
    const newId = filters.colorIdentity.includes(color)
      ? filters.colorIdentity.filter(c => c !== color)
      : [...filters.colorIdentity, color];
    setFilters({ ...filters, colorIdentity: newId });
  };

  const handleSearchChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearch(val);
    if (val.length > 2) {
      const res = await axios.get(`${API_BASE}/cards/autocomplete?q=${val}`);
      setSuggestions(res.data);
    } else { setSuggestions([]); }
  };

  const addCard = async (name: string) => {
    const isExact = name.toLowerCase() === 'island' || name.toLowerCase() === 'swamp' || name.toLowerCase() === 'mountain' || name.toLowerCase() === 'forest' || name.toLowerCase() === 'plains';
    let res = await axios.get(`${API_BASE}/cards/search?q=${encodeURIComponent(name)}${isExact ? '&exact=true' : ''}`);
    if (!res.data || res.data.length === 0) {
        res = await axios.get(`${API_BASE}/cards/search?q=${encodeURIComponent(name)}&lang=de${isExact ? '&exact=true' : ''}`);
    }
    if (res.data && res.data.length > 0) {
      const card = res.data[0];
      await axios.post(`${API_BASE}/collection/add`, { oracle_id: card.oracle_id, name: card.name });
      setSearch(''); setSuggestions([]); refresh();
    }
  };

  const removeCard = async (oracle_id: string) => {
    await axios.post(`${API_BASE}/collection/remove`, { oracle_id });
    refresh();
  };

  const addTag = async (oracle_id: string) => {
    const tagName = newTag[oracle_id];
    if (!tagName) return;
    await axios.post(`${API_BASE}/collection/${oracle_id}/tags`, { tag_name: tagName });
    setNewTag({ ...newTag, [oracle_id]: '' });
    refresh();
    fetchTags();
  };

  const removeTag = async (oracle_id: string, tagName: string) => {
    await axios.delete(`${API_BASE}/collection/${oracle_id}/tags/${tagName}`);
    refresh();
  };

  const addToDeck = async (oracle_id: string) => {
    const action = deckAction[oracle_id];
    if (!action || !action.deckId) return;
    await axios.post(`${API_BASE}/decks/${action.deckId}/add`, { oracle_id, category: action.category });
    setDeckAction({ ...deckAction, [oracle_id]: { ...action, deckId: 0 } });
    refresh();
  };

  const applyFilters = () => {
    const params: any = {};
    if (filters.colors.length > 0) params.colors = filters.colors.join(',');
    if (filters.colorIdentity.length > 0) params.color_identity = filters.colorIdentity.join(',');
    if (filters.format) params.format = filters.format;
    if (filters.type) params.type = filters.type;
    if (filters.keyword) params.keyword = filters.keyword;
    if (filters.set_code) params.set_code = filters.set_code;
    if (filters.tag) params.tag = filters.tag;
    refresh(params);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-8 border-b border-slate-800 shrink-0">
        <div className="flex justify-between items-center mb-8">
            <h1 className="text-3xl font-bold">My Collection</h1>
            <button onClick={() => setDisplayMode(displayMode === 'image' ? 'text' : 'image')} className="flex items-center gap-2 bg-slate-700 px-4 py-2 rounded-lg hover:bg-slate-600 transition">
                {displayMode === 'image' ? <TypeIcon size={20} /> : <Eye size={20} />}
                {displayMode === 'image' ? 'Text Mode' : 'Image Mode'}
            </button>
        </div>
        <div className="flex gap-4 items-start flex-wrap">
            <div className="relative flex-1 min-w-[300px] max-w-2xl">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                <input type="text" value={search} onChange={handleSearchChange} onKeyDown={(e) => e.key === 'Enter' && addCard(search)} placeholder="Add card by name (English or German)..." className="w-full bg-slate-800 border border-slate-700 rounded-xl py-3 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition text-white" />
                {suggestions.length > 0 && (
                <div className="absolute w-full mt-2 bg-slate-800 border border-slate-700 rounded-xl shadow-2xl z-50 max-h-60 overflow-auto text-white">
                    {suggestions.map((s, i) => (<button key={i} onClick={() => addCard(s)} className="w-full text-left px-6 py-3 hover:bg-indigo-600 transition border-b border-slate-700 last:border-0">{s}</button>))}
                </div>
                )}
            </div>
            <div className="flex gap-4 flex-wrap text-white items-center">
                <div className="flex flex-col gap-1">
                    <span className="text-[10px] uppercase text-slate-500 font-bold ml-1">Colors</span>
                    <div className="flex bg-slate-800 border border-slate-700 rounded-lg p-1 gap-1">
                        {['W', 'U', 'B', 'R', 'G'].map(c => (
                            <button
                                key={c}
                                onClick={() => handleColorToggle(c)}
                                className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold transition ${filters.colors.includes(c) ? 'bg-indigo-600 text-white shadow-inner' : 'text-slate-500 hover:bg-slate-700'}`}
                            >
                                {c}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex flex-col gap-1">
                    <span className="text-[10px] uppercase text-slate-500 font-bold ml-1">Color Identity</span>
                    <div className="flex bg-slate-800 border border-slate-700 rounded-lg p-1 gap-1">
                        {['W', 'U', 'B', 'R', 'G'].map(c => (
                            <button
                                key={c}
                                onClick={() => handleIdentityToggle(c)}
                                className={`w-6 h-6 rounded flex items-center justify-center text-xs font-bold transition ${filters.colorIdentity.includes(c) ? 'bg-emerald-600 text-white shadow-inner' : 'text-slate-500 hover:bg-slate-700'}`}
                            >
                                {c}
                            </button>
                        ))}
                    </div>
                </div>
                <select value={filters.format} onChange={e => setFilters({...filters, format: e.target.value})} className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none mt-4"><option value="">All Formats</option><option value="standard">Standard</option><option value="commander">Commander</option><option value="pauper">Pauper</option></select>
                <select value={filters.tag} onChange={e => setFilters({...filters, tag: e.target.value})} className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none w-32 mt-4">
                    <option value="">Filter Tag...</option>
                    {availableTags.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
                <input type="text" placeholder="Set..." value={filters.set_code} onChange={e => setFilters({...filters, set_code: e.target.value})} className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none w-24" />
                <input type="text" placeholder="Keyword..." value={filters.keyword} onChange={e => setFilters({...filters, keyword: e.target.value})} className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none w-32" />
                <button onClick={applyFilters} className="bg-indigo-600 hover:bg-indigo-500 p-2 rounded-lg transition"><Filter size={20} /></button>
            </div>
        </div>
      </div>
      <div className="flex-1 p-8 overflow-auto">
        <div className={`grid ${displayMode === 'image' ? 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5' : 'grid-cols-1'} gap-6`}>
            {collection.map((card) => (
            <div key={card.oracle_id} className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 shadow-lg group transition hover:border-indigo-500 flex flex-col">
                {displayMode === 'image' ? (
                <div className="relative aspect-[1/1.4]">
                    <img src={card.details.image_uris?.normal} alt={card.name} className="w-full h-full object-cover" />
                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition flex flex-col justify-end p-4">
                        <div className="flex justify-between items-center text-white">
                            <span className="font-bold">Qty: {card.quantity}</span>
                            <div className="flex gap-2">
                                <button onClick={() => removeCard(card.oracle_id)} className="bg-rose-600 p-2 rounded-lg hover:bg-rose-500"><Minus size={16} /></button>
                                <button onClick={() => addCard(card.name)} className="bg-indigo-600 p-2 rounded-lg hover:bg-indigo-500"><Plus size={16} /></button>
                            </div>
                        </div>
                    </div>
                </div>
                ) : (
                <div className="p-6 flex justify-between items-center text-white">
                    <div className="flex-1">
                        <div className="flex items-center gap-3"><h3 className="text-xl font-bold text-indigo-400">{card.name}</h3><span className="text-slate-500 text-sm">{card.details.mana_cost}</span></div>
                        <p className="text-slate-400 text-sm line-clamp-1">{card.details.oracle_text}</p>
                        <div className="mt-2 flex gap-2 flex-wrap">
                            {card.tags.map(t => <span key={t} className="text-[10px] bg-slate-700 px-2 py-0.5 rounded uppercase flex items-center gap-1">{t} <X size={10} className="cursor-pointer" onClick={() => removeTag(card.oracle_id, t)} /></span>)}
                            {card.decks.map(d => <span key={d} className="text-[10px] bg-indigo-900 text-white font-bold px-2 py-0.5 rounded uppercase border border-indigo-400 shadow-sm">Deck: {d}</span>)}
                            {card.details.keywords?.slice(0, 3).map(k => <span key={k} className="text-[10px] border border-slate-700 px-2 py-0.5 rounded uppercase text-slate-500">{k}</span>)}
                        </div>
                    </div>
                    <div className="flex items-center gap-6 ml-8">
                        <div className="text-right"><div className="text-xs text-slate-500 uppercase">Qty</div><div className="text-2xl font-bold">{card.quantity}</div></div>
                        <div className="text-right w-24"><div className="text-xs text-slate-500 uppercase">Price</div><div className="text-lg font-bold text-emerald-400">€{parseFloat(card.details.prices?.eur || '0').toFixed(2)}</div></div>
                        <div className="flex flex-col gap-1"><button onClick={() => addCard(card.name)} className="bg-slate-700 p-1 rounded hover:bg-slate-600"><Plus size={14} /></button><button onClick={() => removeCard(card.oracle_id)} className="bg-slate-700 p-1 rounded hover:bg-slate-600"><Minus size={14} /></button></div>
                    </div>
                </div>
                )}
                {/* Deck & Tag Actions */}
                <div className="p-3 border-t border-slate-700/50 space-y-2">
                    <div className="flex gap-1">
                        <select
                            value={deckAction[card.oracle_id]?.deckId || ''}
                            onChange={e => setDeckAction({ ...deckAction, [card.oracle_id]: { deckId: parseInt(e.target.value), category: deckAction[card.oracle_id]?.category || 'Main' } })}
                            className="flex-1 bg-slate-900 border border-slate-700 rounded px-1 py-1 text-[10px] text-white outline-none"
                        >
                            <option value="">Add to Deck...</option>
                            {decks.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
                        </select>
                        <select
                            value={deckAction[card.oracle_id]?.category || 'Main'}
                            onChange={e => setDeckAction({ ...deckAction, [card.oracle_id]: { ...deckAction[card.oracle_id], category: e.target.value } })}
                            className="bg-slate-900 border border-slate-700 rounded px-1 py-1 text-[10px] text-white outline-none"
                        >
                            <option value="Main">Main</option>
                            <option value="Considering">Consid.</option>
                        </select>
                        <button onClick={() => addToDeck(card.oracle_id)} className="bg-indigo-600 p-1 rounded text-white"><Plus size={12} /></button>
                    </div>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            placeholder="New tag..."
                            value={newTag[card.oracle_id] || ''}
                            onChange={e => setNewTag({ ...newTag, [card.oracle_id]: e.target.value })}
                            onKeyDown={e => e.key === 'Enter' && addTag(card.oracle_id)}
                            className="flex-1 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-xs text-white outline-none focus:border-indigo-500"
                        />
                        <button onClick={() => addTag(card.oracle_id)} className="text-indigo-400 hover:text-indigo-300 transition"><TagIcon size={14} /></button>
                    </div>
                </div>
            </div>
            ))}
        </div>
      </div>
    </div>
  );
};

const DecksView = ({ decks, selectedDeck, setSelectedDeck, refresh }: { decks: Deck[], selectedDeck: Deck | null, setSelectedDeck: (d: Deck | null) => void, refresh: () => void }) => {
    const [deckDetails, setDeckDetails] = useState<DeckDetails | null>(null);
    const [newDeckName, setNewDeckName] = useState('');
    const [cardSearch, setCardSearch] = useState('');
    const [cardSuggestions, setCardSuggestions] = useState<string[]>([]);
    const [category, setCategory] = useState('Main');

    useEffect(() => { if (selectedDeck) fetchDeckDetails(selectedDeck.id); }, [selectedDeck]);
    const fetchDeckDetails = async (id: number) => { const res = await axios.get(`${API_BASE}/decks/${id}`); setDeckDetails(res.data); };
    const createDeck = async () => { if (!newDeckName) return; await axios.post(`${API_BASE}/decks`, { name: newDeckName }); setNewDeckName(''); refresh(); };
    const handleCardSearchChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const val = e.target.value; setCardSearch(val);
        if (val.length > 2) { const res = await axios.get(`${API_BASE}/cards/autocomplete?q=${val}`); setCardSuggestions(res.data); } else { setCardSuggestions([]); }
    };

    const addCardToDeck = async (name: string) => {
        const isExact = name.toLowerCase() === 'island' || name.toLowerCase() === 'swamp' || name.toLowerCase() === 'mountain' || name.toLowerCase() === 'forest' || name.toLowerCase() === 'plains';
        const res = await axios.get(`${API_BASE}/cards/search?q=${encodeURIComponent(name)}${isExact ? '&exact=true' : ''}`);
        if (res.data && res.data.length > 0 && selectedDeck) {
            const card = res.data[0];
            await axios.post(`${API_BASE}/collection/add`, { oracle_id: card.oracle_id, name: card.name });
            await axios.post(`${API_BASE}/decks/${selectedDeck.id}/add`, { oracle_id: card.oracle_id, category });
            setCardSearch(''); setCardSuggestions([]); fetchDeckDetails(selectedDeck.id);
        }
    };

    const removeCardFromDeck = async (oracle_id: string, cat: string) => {
        if (!selectedDeck) return;
        await axios.post(`${API_BASE}/decks/${selectedDeck.id}/remove`, { oracle_id, category: cat });
        fetchDeckDetails(selectedDeck.id);
    };

    return (
        <div className="p-8 h-full overflow-auto">
            {!selectedDeck ? (
                <div>
                    <h1 className="text-3xl font-bold mb-8 text-white">My Decks</h1>
                    <div className="flex gap-4 mb-8">
                        <input type="text" value={newDeckName} onChange={(e) => setNewDeckName(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && createDeck()} placeholder="New deck name..." className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none text-white" />
                        <button onClick={createDeck} className="bg-indigo-600 hover:bg-indigo-500 px-6 py-2 rounded-lg flex items-center gap-2 transition text-white"><Plus size={20} /> Create Deck</button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {decks.map(deck => (
                            <button key={deck.id} onClick={() => setSelectedDeck(deck)} className="bg-slate-800 p-6 rounded-xl border border-slate-700 text-left hover:border-indigo-500 transition group">
                                <div className="flex justify-between items-center"><h3 className="text-xl font-bold group-hover:text-indigo-400 transition text-white">{deck.name}</h3><ChevronRight className="text-slate-600 group-hover:text-indigo-400 transition" /></div>
                                <p className="text-slate-500 mt-2">{deck.description || 'No description'}</p>
                            </button>
                        ))}
                    </div>
                </div>
            ) : (
                <div className="flex flex-col h-full">
                    <button onClick={() => {setSelectedDeck(null); setDeckDetails(null);}} className="text-indigo-400 hover:text-indigo-300 mb-4 flex items-center gap-1 shrink-0">← Back</button>
                    <div className="flex justify-between items-center mb-8 shrink-0 flex-wrap gap-4 text-white">
                        <h1 className="text-4xl font-black">{selectedDeck.name}</h1>
                        <div className="flex gap-2">
                            <select value={category} onChange={e => setCategory(e.target.value)} className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm focus:outline-none"><option value="Main">Mainboard</option><option value="Considering">Considering</option><option value="History">History</option></select>
                            <div className="relative">
                                <input type="text" value={cardSearch} onChange={handleCardSearchChange} onKeyDown={(e) => e.key === 'Enter' && addCardToDeck(cardSearch)} placeholder="Add card..." className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 focus:outline-none text-white" />
                                {cardSuggestions.length > 0 && (<div className="absolute w-full mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl z-50 overflow-hidden">{cardSuggestions.map((s, i) => (<button key={i} onClick={() => addCardToDeck(s)} className="w-full text-left px-4 py-2 hover:bg-indigo-600 text-sm border-b border-slate-700 last:border-0 text-white">{s}</button>))}</div>)}
                            </div>
                        </div>
                    </div>
                    {deckDetails && (
                        <div className="space-y-8 pb-8 text-white">
                            {['Main', 'Considering', 'History'].map(cat => {
                                const catCards = deckDetails.cards.filter(c => c.category === cat);
                                if (catCards.length === 0) return null;
                                const typedCards = catCards.reduce((acc: Record<string, DeckDetailCard[]>, c) => {
                                    const type = c.details.type_line?.split('—')[0].trim().split(' ')[0] || 'Unknown';
                                    if (!acc[type]) acc[type] = []; acc[type].push(c); return acc;
                                }, {});
                                return (
                                    <div key={cat} className="bg-slate-800/30 p-6 rounded-2xl border border-slate-800">
                                        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2"><div className="w-2 h-8 bg-indigo-500 rounded-full" />{cat} ({catCards.reduce((sum, c) => sum + c.quantity, 0)})</h2>
                                        <div className="space-y-6">
                                            {Object.entries(typedCards).map(([type, cards]) => (
                                                <div key={type}>
                                                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 border-b border-slate-700/50 pb-1">{type} ({cards.reduce((sum, c) => sum + c.quantity, 0)})</h3>
                                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                                        {cards.map((c, i) => (
                                                            <div key={i} className="flex justify-between items-center bg-slate-800 p-3 rounded-xl border border-slate-700 hover:border-slate-500 transition group">
                                                                <div className="flex items-center gap-3">
                                                                    <span className="text-indigo-400 font-black">{c.quantity}x</span>
                                                                    <span className="font-semibold text-sm">{c.name}</span>
                                                                </div>
                                                                <div className="flex items-center gap-3">
                                                                    <span className="text-slate-500 font-mono text-[10px]">{c.details.mana_cost}</span>
                                                                    <button onClick={() => removeCardFromDeck(c.oracle_id, cat)} className="text-slate-600 hover:text-rose-500 transition"><X size={14} /></button>
                                                                </div>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const StatsView = ({ stats }: { stats: Stats }) => {
    const data = stats.history.map(h => ({ date: new Date(h.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), value: h.value }));
    return (
        <div className="p-8 h-full overflow-auto">
            <h1 className="text-3xl font-bold mb-8 text-white">Statistics</h1>
            <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700 mb-12">
                <div className="text-slate-500 uppercase text-sm font-semibold mb-2">Total Value</div>
                <div className="text-5xl font-black text-emerald-400">€{stats.total_value.toFixed(2)}</div>
                <div className="text-slate-500 mt-4 text-sm">Cheapest printing {'>'} €1.00</div>
            </div>
            <div className="bg-slate-800 p-8 rounded-2xl border border-slate-700">
                <h3 className="text-xl font-bold mb-8 text-white">Value History</h3>
                <div className="h-[400px] w-full">
                    <ResponsiveContainer width="100%" height="100%"><LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#334155" /><XAxis dataKey="date" stroke="#94a3b8" /><YAxis stroke="#94a3b8" /><Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }} itemStyle={{ color: '#10b981' }} /><Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981' }} activeDot={{ r: 8 }} /></LineChart></ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default App;
