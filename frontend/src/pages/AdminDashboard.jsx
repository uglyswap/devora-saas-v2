import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import Navigation from '../components/Navigation';
import {
  User, Mail, Calendar, Euro, Shield, ShieldOff,
  Trash2, Gift, CreditCard, FolderOpen, X,
  Save, Plus, Minus, Ban, CheckCircle, Search, Settings,
  UserPlus, Copy, RefreshCw, Edit, TrendingUp, TrendingDown,
  Activity, AlertTriangle, Bell, Download, BarChart3, Users,
  DollarSign, Clock, Zap, ArrowUpRight, ArrowDownRight,
  PieChart, LineChart, Filter, MoreVertical, ExternalLink
} from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { toast } from 'sonner';
import {
  LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  PieChart as RechartsPieChart, Pie, Cell, Legend
} from 'recharts';

const API = process.env.REACT_APP_BACKEND_URL + '/api';

// Chart colors
const CHART_COLORS = {
  primary: '#10b981',
  secondary: '#3b82f6',
  tertiary: '#8b5cf6',
  danger: '#ef4444',
  warning: '#f59e0b'
};

const PIE_COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'];

export default function AdminDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // State
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [config, setConfig] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [realtimeData, setRealtimeData] = useState({
    activeUsers: 0,
    requestsPerMinute: 0,
    errorRate: 0,
    avgResponseTime: 0
  });

  // Charts data
  const [revenueChartData, setRevenueChartData] = useState([]);
  const [userGrowthData, setUserGrowthData] = useState([]);
  const [subscriptionDistribution, setSubscriptionDistribution] = useState([]);

  // UI State
  const [selectedUser, setSelectedUser] = useState(null);
  const [activeSection, setActiveSection] = useState('overview');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState('30d');
  const [saving, setSaving] = useState(false);

  // Modal states
  const [showAddUserForm, setShowAddUserForm] = useState(false);
  const [showEditStatusModal, setShowEditStatusModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  // New user form
  const [newUserEmail, setNewUserEmail] = useState('');
  const [newUserName, setNewUserName] = useState('');
  const [newUserPassword, setNewUserPassword] = useState('');
  const [newUserStatus, setNewUserStatus] = useState('trialing');
  const [newUserIsAdmin, setNewUserIsAdmin] = useState(false);
  const [creatingUser, setCreatingUser] = useState(false);

  // WebSocket ref for realtime
  const wsRef = useRef(null);

  // Check admin access
  useEffect(() => {
    if (!user?.is_admin) {
      navigate('/');
      return;
    }
    loadAllData();
    setupWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user, navigate]);

  // Setup WebSocket for realtime data
  const setupWebSocket = () => {
    try {
      const wsUrl = API.replace('http', 'ws').replace('/api', '/ws/admin');
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'realtime_stats') {
          setRealtimeData(data.stats);
        } else if (data.type === 'alert') {
          setAlerts(prev => [data.alert, ...prev.slice(0, 9)]);
        }
      };

      wsRef.current.onerror = () => {
        console.log('WebSocket not available, using polling');
        // Fallback to polling
        const pollInterval = setInterval(() => {
          fetchRealtimeStats();
        }, 30000);
        return () => clearInterval(pollInterval);
      };
    } catch (error) {
      console.log('WebSocket setup failed, using polling');
    }
  };

  // Fetch realtime stats (fallback)
  const fetchRealtimeStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/admin/realtime-stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRealtimeData(data);
      }
    } catch (error) {
      console.error('Error fetching realtime stats:', error);
    }
  };

  // Load all admin data
  const loadAllData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Parallel fetch
      const [statsRes, usersRes, configRes] = await Promise.all([
        fetch(`${API}/admin/stats`, { headers }),
        fetch(`${API}/admin/users?limit=1000`, { headers }),
        fetch(`${API}/admin/config`, { headers })
      ]);

      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
        generateChartData(statsData);
      }

      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(usersData.users);
        calculateSubscriptionDistribution(usersData.users);
      }

      if (configRes.ok) {
        setConfig(await configRes.json());
      }

      // Generate mock alerts
      generateMockAlerts();

    } catch (error) {
      console.error('Error loading admin data:', error);
      toast.error('Erreur lors du chargement des donnees');
    } finally {
      setLoading(false);
    }
  };

  // Generate chart data from stats
  const generateChartData = (statsData) => {
    // Revenue chart (last 12 months mock data - would come from API)
    const months = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec'];
    const currentMonth = new Date().getMonth();

    const revenueData = months.slice(0, currentMonth + 1).map((month, i) => ({
      month,
      revenue: Math.floor(Math.random() * 5000) + statsData.revenue_current_month * 0.8,
      mrr: Math.floor(Math.random() * 3000) + statsData.active_subscriptions * 9.90
    }));
    revenueData[currentMonth] = {
      month: months[currentMonth],
      revenue: statsData.revenue_current_month,
      mrr: statsData.active_subscriptions * 9.90
    };
    setRevenueChartData(revenueData);

    // User growth (last 30 days mock)
    const growthData = [];
    for (let i = 30; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      growthData.push({
        date: date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }),
        users: Math.floor(statsData.total_users * (1 - i * 0.01)),
        active: Math.floor(statsData.active_subscriptions * (1 - i * 0.008))
      });
    }
    setUserGrowthData(growthData);
  };

  // Calculate subscription distribution
  const calculateSubscriptionDistribution = (usersData) => {
    const distribution = usersData.reduce((acc, u) => {
      const status = u.subscription_status || 'none';
      acc[status] = (acc[status] || 0) + 1;
      return acc;
    }, {});

    setSubscriptionDistribution(
      Object.entries(distribution).map(([name, value]) => ({ name, value }))
    );
  };

  // Generate mock alerts
  const generateMockAlerts = () => {
    setAlerts([
      { id: 1, type: 'warning', message: '3 echecs de paiement detectes', time: 'Il y a 2h' },
      { id: 2, type: 'info', message: 'Nouveau pic de trafic: +45%', time: 'Il y a 4h' },
      { id: 3, type: 'success', message: '5 nouveaux abonnes aujourd\'hui', time: 'Il y a 6h' }
    ]);
  };

  // User operations
  const loadUserInvoices = async (userId) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/admin/users/${userId}/invoices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        return await response.json();
      }
      return { invoices: [], total_paid: 0 };
    } catch (error) {
      console.error('Error loading invoices:', error);
      return { invoices: [], total_paid: 0 };
    }
  };

  // Get total paid for user - FIXED: Now async with real API call
  const [userTotals, setUserTotals] = useState({});

  const fetchUserTotal = async (userId) => {
    if (userTotals[userId] !== undefined) return;

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/admin/users/${userId}/invoices`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setUserTotals(prev => ({ ...prev, [userId]: data.total_paid || 0 }));
      }
    } catch (error) {
      setUserTotals(prev => ({ ...prev, [userId]: 0 }));
    }
  };

  // Fetch totals for visible users
  useEffect(() => {
    const filteredUsers = users.filter(u =>
      u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (u.full_name && u.full_name.toLowerCase().includes(searchTerm.toLowerCase()))
    ).slice(0, 20);

    filteredUsers.forEach(u => {
      if (userTotals[u.id] === undefined) {
        fetchUserTotal(u.id);
      }
    });
  }, [users, searchTerm]);

  // Create new user
  const createNewUser = async () => {
    if (!newUserEmail || !newUserName || !newUserPassword) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }

    setCreatingUser(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/admin/users`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: newUserEmail,
          name: newUserName,
          password: newUserPassword,
          subscription_status: newUserStatus,
          is_admin: newUserIsAdmin
        })
      });

      if (response.ok) {
        toast.success('Utilisateur cree avec succes');
        setShowAddUserForm(false);
        resetNewUserForm();
        loadAllData();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erreur lors de la creation');
      }
    } catch (error) {
      console.error('Error creating user:', error);
      toast.error('Erreur lors de la creation');
    } finally {
      setCreatingUser(false);
    }
  };

  const resetNewUserForm = () => {
    setNewUserEmail('');
    setNewUserName('');
    setNewUserPassword('');
    setNewUserStatus('trialing');
    setNewUserIsAdmin(false);
  };

  const generatePassword = () => {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setNewUserPassword(password);
    toast.success('Mot de passe genere!');
  };

  // Save config
  const saveConfig = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API}/admin/config`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          stripe_api_key: config.stripe_api_key || null,
          stripe_webhook_secret: config.stripe_webhook_secret || null,
          stripe_test_mode: config.stripe_test_mode,
          resend_api_key: config.resend_api_key || null,
          resend_from_email: config.resend_from_email,
          subscription_price: parseFloat(config.subscription_price),
          free_trial_days: parseInt(config.free_trial_days),
          max_failed_payments: parseInt(config.max_failed_payments)
        })
      });

      if (response.ok) {
        setConfig(await response.json());
        toast.success('Configuration sauvegardee!');
      } else {
        toast.error('Erreur lors de la sauvegarde');
      }
    } catch (error) {
      console.error('Error saving config:', error);
      toast.error('Erreur lors de la sauvegarde');
    }
    setSaving(false);
  };

  // Export data
  const exportData = (type) => {
    let data, filename;

    if (type === 'users') {
      data = users.map(u => ({
        email: u.email,
        name: u.full_name,
        status: u.subscription_status,
        created: u.created_at,
        is_admin: u.is_admin
      }));
      filename = 'users_export.csv';
    } else if (type === 'revenue') {
      data = revenueChartData;
      filename = 'revenue_export.csv';
    }

    const csv = convertToCSV(data);
    downloadCSV(csv, filename);
    toast.success(`Export ${type} telecharge!`);
  };

  const convertToCSV = (data) => {
    if (!data.length) return '';
    const headers = Object.keys(data[0]).join(',');
    const rows = data.map(obj => Object.values(obj).join(','));
    return [headers, ...rows].join('\n');
  };

  const downloadCSV = (csv, filename) => {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Filter users
  const filteredUsers = users.filter(u =>
    u.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (u.full_name && u.full_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0a0a0b] via-[#111113] to-[#0a0a0b] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-400">Chargement du dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a0b] via-[#111113] to-[#0a0a0b]">
      <Navigation />

      <div className="max-w-[1600px] mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white">Dashboard Admin</h1>
            <p className="text-gray-400 mt-1">Vue d'ensemble et analytics en temps reel</p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
            >
              <option value="7d">7 derniers jours</option>
              <option value="30d">30 derniers jours</option>
              <option value="90d">90 derniers jours</option>
              <option value="1y">Cette annee</option>
            </select>
            <Button variant="outline" onClick={loadAllData}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Rafraichir
            </Button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex gap-2 mb-8 overflow-x-auto">
          {[
            { id: 'overview', label: 'Vue d\'ensemble', icon: BarChart3 },
            { id: 'users', label: 'Utilisateurs', icon: Users },
            { id: 'revenue', label: 'Revenus', icon: DollarSign },
            { id: 'config', label: 'Configuration', icon: Settings },
            { id: 'alerts', label: 'Alertes', icon: Bell }
          ].map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSection(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors whitespace-nowrap ${activeSection === tab.id
                    ? 'bg-emerald-600 text-white'
                    : 'bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                  }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* OVERVIEW SECTION */}
        {activeSection === 'overview' && (
          <div className="space-y-6">
            {/* Realtime Metrics */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border border-emerald-500/30 rounded-xl p-4">
                <div className="flex items-center justify-between">
                  <Activity className="w-5 h-5 text-emerald-400" />
                  <span className="text-xs text-emerald-400 flex items-center gap-1">
                    <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                    Live
                  </span>
                </div>
                <p className="text-2xl font-bold text-white mt-2">{realtimeData.activeUsers}</p>
                <p className="text-sm text-gray-400">Utilisateurs en ligne</p>
              </div>

              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 rounded-xl p-4">
                <Zap className="w-5 h-5 text-blue-400" />
                <p className="text-2xl font-bold text-white mt-2">{realtimeData.requestsPerMinute}</p>
                <p className="text-sm text-gray-400">Requetes/min</p>
              </div>

              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-xl p-4">
                <Clock className="w-5 h-5 text-purple-400" />
                <p className="text-2xl font-bold text-white mt-2">{realtimeData.avgResponseTime}ms</p>
                <p className="text-sm text-gray-400">Temps reponse moyen</p>
              </div>

              <div className={`bg-gradient-to-br ${realtimeData.errorRate > 5
                  ? 'from-red-500/20 to-red-600/10 border-red-500/30'
                  : 'from-green-500/20 to-green-600/10 border-green-500/30'
                } border rounded-xl p-4`}>
                <AlertTriangle className={`w-5 h-5 ${realtimeData.errorRate > 5 ? 'text-red-400' : 'text-green-400'}`} />
                <p className="text-2xl font-bold text-white mt-2">{realtimeData.errorRate}%</p>
                <p className="text-sm text-gray-400">Taux d'erreur</p>
              </div>
            </div>

            {/* Main KPIs */}
            {stats && (
              <div className="grid grid-cols-4 gap-6">
                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Users className="w-8 h-8 text-blue-400" />
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded-full">
                      +{stats.new_users_this_month} ce mois
                    </span>
                  </div>
                  <p className="text-3xl font-bold text-white">{stats.total_users}</p>
                  <p className="text-gray-400">Utilisateurs totaux</p>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <CheckCircle className="w-8 h-8 text-emerald-400" />
                    <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded-full flex items-center gap-1">
                      <ArrowUpRight className="w-3 h-3" />
                      {((stats.active_subscriptions / stats.total_users) * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-3xl font-bold text-white">{stats.active_subscriptions}</p>
                  <p className="text-gray-400">Abonnements actifs</p>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <Euro className="w-8 h-8 text-yellow-400" />
                    <span className="text-xs bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded-full">
                      MRR: {(stats.active_subscriptions * 9.90).toFixed(0)}
                    </span>
                  </div>
                  <p className="text-3xl font-bold text-white">{stats.total_revenue.toFixed(0)}€</p>
                  <p className="text-gray-400">Revenu total</p>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <TrendingDown className="w-8 h-8 text-red-400" />
                    <span className={`text-xs px-2 py-1 rounded-full ${stats.churn_rate > 5
                        ? 'bg-red-500/20 text-red-400'
                        : 'bg-green-500/20 text-green-400'
                      }`}>
                      {stats.churn_rate > 5 ? 'Attention' : 'OK'}
                    </span>
                  </div>
                  <p className="text-3xl font-bold text-white">{stats.churn_rate}%</p>
                  <p className="text-gray-400">Taux de churn</p>
                </div>
              </div>
            )}

            {/* Charts Row */}
            <div className="grid grid-cols-2 gap-6">
              {/* Revenue Chart */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-white">Evolution des revenus</h3>
                  <Button variant="ghost" size="sm" onClick={() => exportData('revenue')}>
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={revenueChartData}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="month" stroke="#666" />
                    <YAxis stroke="#666" />
                    <Tooltip
                      contentStyle={{ background: '#1a1a1d', border: '1px solid #333', borderRadius: '8px' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke={CHART_COLORS.primary}
                      fillOpacity={1}
                      fill="url(#colorRevenue)"
                    />
                    <Line type="monotone" dataKey="mrr" stroke={CHART_COLORS.secondary} strokeDasharray="5 5" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* User Growth Chart */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Croissance utilisateurs</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <RechartsLineChart data={userGrowthData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                    <XAxis dataKey="date" stroke="#666" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#666" />
                    <Tooltip
                      contentStyle={{ background: '#1a1a1d', border: '1px solid #333', borderRadius: '8px' }}
                      labelStyle={{ color: '#fff' }}
                    />
                    <Line type="monotone" dataKey="users" stroke={CHART_COLORS.secondary} strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="active" stroke={CHART_COLORS.primary} strokeWidth={2} dot={false} />
                  </RechartsLineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-3 gap-6">
              {/* Subscription Distribution */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Repartition abonnements</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <RechartsPieChart>
                    <Pie
                      data={subscriptionDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {subscriptionDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ background: '#1a1a1d', border: '1px solid #333', borderRadius: '8px' }}
                    />
                    <Legend />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </div>

              {/* Recent Alerts */}
              <div className="col-span-2 bg-white/5 border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white">Alertes recentes</h3>
                  <Button variant="ghost" size="sm" onClick={() => setActiveSection('alerts')}>
                    Voir tout
                  </Button>
                </div>
                <div className="space-y-3">
                  {alerts.slice(0, 3).map(alert => (
                    <div
                      key={alert.id}
                      className={`flex items-center gap-3 p-3 rounded-lg ${alert.type === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                          alert.type === 'success' ? 'bg-green-500/10 border border-green-500/30' :
                            'bg-blue-500/10 border border-blue-500/30'
                        }`}
                    >
                      <div className={`w-2 h-2 rounded-full ${alert.type === 'warning' ? 'bg-yellow-500' :
                          alert.type === 'success' ? 'bg-green-500' :
                            'bg-blue-500'
                        }`} />
                      <span className="flex-1 text-sm text-gray-200">{alert.message}</span>
                      <span className="text-xs text-gray-500">{alert.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* USERS SECTION */}
        {activeSection === 'users' && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Gestion des utilisateurs</h2>
              <div className="flex items-center gap-4">
                <Button
                  onClick={() => setShowAddUserForm(!showAddUserForm)}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  <UserPlus className="w-4 h-4 mr-2" />
                  Ajouter
                </Button>
                <Button variant="outline" onClick={() => exportData('users')}>
                  <Download className="w-4 h-4 mr-2" />
                  Exporter
                </Button>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <Input
                    placeholder="Rechercher..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 w-64 bg-white/5 border-white/10"
                  />
                </div>
              </div>
            </div>

            {/* Add User Form */}
            {showAddUserForm && (
              <div className="mb-6 p-6 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                <h3 className="text-lg font-semibold text-emerald-400 mb-4">Creer un utilisateur</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-gray-300">Email</Label>
                    <Input
                      type="email"
                      value={newUserEmail}
                      onChange={(e) => setNewUserEmail(e.target.value)}
                      placeholder="email@example.com"
                      className="bg-white/5 border-white/10 mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-gray-300">Nom</Label>
                    <Input
                      value={newUserName}
                      onChange={(e) => setNewUserName(e.target.value)}
                      placeholder="Jean Dupont"
                      className="bg-white/5 border-white/10 mt-1"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label className="text-gray-300">Mot de passe</Label>
                    <div className="flex gap-2 mt-1">
                      <Input
                        value={newUserPassword}
                        onChange={(e) => setNewUserPassword(e.target.value)}
                        className="bg-white/5 border-white/10 flex-1"
                      />
                      <Button onClick={generatePassword} variant="outline">
                        <RefreshCw className="w-4 h-4 mr-2" />
                        Generer
                      </Button>
                      <Button onClick={() => { navigator.clipboard.writeText(newUserPassword); toast.success('Copie!'); }} variant="outline">
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div>
                    <Label className="text-gray-300">Statut</Label>
                    <select
                      value={newUserStatus}
                      onChange={(e) => setNewUserStatus(e.target.value)}
                      className="w-full mt-1 px-3 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                    >
                      <option value="trialing" className="bg-gray-800">Essai</option>
                      <option value="active" className="bg-gray-800">Actif</option>
                    </select>
                  </div>
                  <div className="flex items-end">
                    <label className="flex items-center gap-2 text-gray-300">
                      <input
                        type="checkbox"
                        checked={newUserIsAdmin}
                        onChange={(e) => setNewUserIsAdmin(e.target.checked)}
                        className="w-4 h-4"
                      />
                      Administrateur
                    </label>
                  </div>
                </div>
                <div className="flex gap-3 mt-6">
                  <Button onClick={createNewUser} disabled={creatingUser} className="bg-emerald-600 hover:bg-emerald-700">
                    {creatingUser ? 'Creation...' : 'Creer'}
                  </Button>
                  <Button onClick={() => { setShowAddUserForm(false); resetNewUserForm(); }} variant="outline">
                    Annuler
                  </Button>
                </div>
              </div>
            )}

            {/* Users Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Email</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Nom</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Inscription</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Total Paye</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Statut</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Role</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-400">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredUsers.slice(0, 50).map(u => (
                    <tr
                      key={u.id}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-3 px-4 text-sm text-gray-300">{u.email}</td>
                      <td className="py-3 px-4 text-sm text-gray-300">{u.full_name || '-'}</td>
                      <td className="py-3 px-4 text-sm text-gray-400">
                        {new Date(u.created_at).toLocaleDateString('fr-FR')}
                      </td>
                      <td className="py-3 px-4 text-sm font-semibold text-emerald-400">
                        {userTotals[u.id] !== undefined
                          ? `${userTotals[u.id].toFixed(2)}€`
                          : <span className="text-gray-500">...</span>
                        }
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${u.subscription_status === 'active' ? 'bg-green-500/20 text-green-400' :
                            u.subscription_status === 'trialing' ? 'bg-blue-500/20 text-blue-400' :
                              u.subscription_status === 'past_due' ? 'bg-orange-500/20 text-orange-400' :
                                'bg-gray-500/20 text-gray-400'
                          }`}>
                          {u.subscription_status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {u.is_admin && (
                          <span className="px-2 py-1 rounded-full text-xs bg-yellow-500/20 text-yellow-400">
                            Admin
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setSelectedUser(u)}
                            className="text-blue-400 hover:text-blue-300"
                          >
                            Details
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {filteredUsers.length > 50 && (
              <p className="text-center text-gray-400 mt-4">
                Affichage de 50/{filteredUsers.length} utilisateurs. Utilisez la recherche pour filtrer.
              </p>
            )}
          </div>
        )}

        {/* REVENUE SECTION */}
        {activeSection === 'revenue' && stats && (
          <div className="space-y-6">
            {/* Revenue KPIs */}
            <div className="grid grid-cols-4 gap-6">
              <div className="bg-gradient-to-br from-emerald-500/20 to-emerald-600/10 border border-emerald-500/30 rounded-xl p-6">
                <Euro className="w-8 h-8 text-emerald-400 mb-4" />
                <p className="text-3xl font-bold text-white">{stats.revenue_current_month.toFixed(2)}€</p>
                <p className="text-gray-400">Revenu ce mois</p>
              </div>
              <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/10 border border-blue-500/30 rounded-xl p-6">
                <TrendingUp className="w-8 h-8 text-blue-400 mb-4" />
                <p className="text-3xl font-bold text-white">{(stats.active_subscriptions * 9.90).toFixed(2)}€</p>
                <p className="text-gray-400">MRR</p>
              </div>
              <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/10 border border-purple-500/30 rounded-xl p-6">
                <DollarSign className="w-8 h-8 text-purple-400 mb-4" />
                <p className="text-3xl font-bold text-white">{stats.total_revenue.toFixed(2)}€</p>
                <p className="text-gray-400">Revenu total</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-500/20 to-yellow-600/10 border border-yellow-500/30 rounded-xl p-6">
                <PieChart className="w-8 h-8 text-yellow-400 mb-4" />
                <p className="text-3xl font-bold text-white">{stats.revenue_last_month.toFixed(2)}€</p>
                <p className="text-gray-400">Mois dernier</p>
              </div>
            </div>

            {/* Full width revenue chart */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-6">Historique des revenus</h3>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={revenueChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="month" stroke="#666" />
                  <YAxis stroke="#666" />
                  <Tooltip
                    contentStyle={{ background: '#1a1a1d', border: '1px solid #333', borderRadius: '8px' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Bar dataKey="revenue" fill={CHART_COLORS.primary} radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* CONFIG SECTION */}
        {activeSection === 'config' && config && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-8">
            <h2 className="text-2xl font-bold text-white mb-6">Configuration Systeme</h2>

            {/* Stripe */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <CreditCard className="w-5 h-5 text-blue-400" />
                Stripe
              </h3>
              <div className="space-y-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={config.stripe_test_mode}
                    onChange={(e) => setConfig({ ...config, stripe_test_mode: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <span className="text-gray-300">Mode Test</span>
                </label>
                <div>
                  <Label className="text-gray-300">API Key</Label>
                  <Input
                    type="password"
                    value={config.stripe_api_key || ''}
                    onChange={(e) => setConfig({ ...config, stripe_api_key: e.target.value })}
                    placeholder={config.stripe_test_mode ? 'sk_test_...' : 'sk_live_...'}
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
                <div>
                  <Label className="text-gray-300">Webhook Secret</Label>
                  <Input
                    type="password"
                    value={config.stripe_webhook_secret || ''}
                    onChange={(e) => setConfig({ ...config, stripe_webhook_secret: e.target.value })}
                    placeholder="whsec_..."
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
              </div>
            </div>

            {/* Billing */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Euro className="w-5 h-5 text-yellow-400" />
                Facturation
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label className="text-gray-300">Prix abonnement (EUR TTC)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={config.subscription_price}
                    onChange={(e) => setConfig({ ...config, subscription_price: e.target.value })}
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
                <div>
                  <Label className="text-gray-300">Jours essai gratuit</Label>
                  <Input
                    type="number"
                    value={config.free_trial_days}
                    onChange={(e) => setConfig({ ...config, free_trial_days: e.target.value })}
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
                <div>
                  <Label className="text-gray-300">Echecs max avant blocage</Label>
                  <Input
                    type="number"
                    value={config.max_failed_payments}
                    onChange={(e) => setConfig({ ...config, max_failed_payments: e.target.value })}
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
              </div>
            </div>

            {/* Email */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Mail className="w-5 h-5 text-purple-400" />
                Email (Resend)
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-gray-300">API Key</Label>
                  <Input
                    type="password"
                    value={config.resend_api_key || ''}
                    onChange={(e) => setConfig({ ...config, resend_api_key: e.target.value })}
                    placeholder="re_..."
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
                <div>
                  <Label className="text-gray-300">Email expediteur</Label>
                  <Input
                    type="email"
                    value={config.resend_from_email || ''}
                    onChange={(e) => setConfig({ ...config, resend_from_email: e.target.value })}
                    className="bg-white/5 border-white/10 mt-1"
                  />
                </div>
              </div>
            </div>

            <Button onClick={saveConfig} disabled={saving} className="bg-emerald-600 hover:bg-emerald-700">
              <Save className="w-4 h-4 mr-2" />
              {saving ? 'Sauvegarde...' : 'Sauvegarder'}
            </Button>
          </div>
        )}

        {/* ALERTS SECTION */}
        {activeSection === 'alerts' && (
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Alertes systeme</h2>
              <Button variant="outline" onClick={() => setAlerts([])}>
                Tout effacer
              </Button>
            </div>

            {alerts.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <Bell className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Aucune alerte</p>
              </div>
            ) : (
              <div className="space-y-3">
                {alerts.map(alert => (
                  <div
                    key={alert.id}
                    className={`flex items-center gap-4 p-4 rounded-lg ${alert.type === 'warning' ? 'bg-yellow-500/10 border border-yellow-500/30' :
                        alert.type === 'success' ? 'bg-green-500/10 border border-green-500/30' :
                          alert.type === 'error' ? 'bg-red-500/10 border border-red-500/30' :
                            'bg-blue-500/10 border border-blue-500/30'
                      }`}
                  >
                    {alert.type === 'warning' && <AlertTriangle className="w-5 h-5 text-yellow-400" />}
                    {alert.type === 'success' && <CheckCircle className="w-5 h-5 text-green-400" />}
                    {alert.type === 'error' && <X className="w-5 h-5 text-red-400" />}
                    {alert.type === 'info' && <Activity className="w-5 h-5 text-blue-400" />}
                    <div className="flex-1">
                      <p className="text-white">{alert.message}</p>
                      <p className="text-sm text-gray-400">{alert.time}</p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setAlerts(prev => prev.filter(a => a.id !== alert.id))}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* User Details Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1a1a1d] border border-white/10 rounded-xl max-w-2xl w-full max-h-[80vh] overflow-auto">
            <div className="p-6 border-b border-white/10 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-white">{selectedUser.email}</h2>
                <p className="text-sm text-gray-400">
                  Inscrit le {new Date(selectedUser.created_at).toLocaleDateString('fr-FR')}
                </p>
              </div>
              <Button variant="ghost" onClick={() => setSelectedUser(null)}>
                <X className="w-5 h-5" />
              </Button>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <p className="text-sm text-gray-400">Nom</p>
                  <p className="text-white">{selectedUser.full_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Statut</p>
                  <span className={`px-2 py-1 rounded-full text-xs ${selectedUser.subscription_status === 'active' ? 'bg-green-500/20 text-green-400' :
                      selectedUser.subscription_status === 'trialing' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-gray-500/20 text-gray-400'
                    }`}>
                    {selectedUser.subscription_status}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Total paye</p>
                  <p className="text-emerald-400 font-semibold">
                    {userTotals[selectedUser.id]?.toFixed(2) || '0.00'}€
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Admin</p>
                  <p className="text-white">{selectedUser.is_admin ? 'Oui' : 'Non'}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
