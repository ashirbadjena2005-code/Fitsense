import React from 'react';
import { useAuth } from '@/hooks/use-auth';

type CardProps = {
  children?: React.ReactNode;
  className?: string;
};

type TabsProps = {
  children?: React.ReactNode;
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
};

type TabsListProps = {
  children?: React.ReactNode;
  className?: string;
};

type TabsTriggerProps = {
  children?: React.ReactNode;
  value: string;
};

type TabsContentProps = {
  children?: React.ReactNode;
  value: string;
  className?: string;
};

type ButtonProps = {
  children?: React.ReactNode;
  variant?: string;
  size?: string;
  onClick?: () => void;
  className?: string;
};

type BadgeProps = {
  children?: React.ReactNode;
  variant?: string;
  className?: string;
};

type ProgressProps = {
  value: number;
  className?: string;
};

// --- UI COMPONENTS (inspired by shadcn/ui) ---
// These are self-contained functional components with Tailwind CSS for styling.

const Card: React.FC<CardProps> = ({ children, className = "" }) => (
  <div className={`bg-white border rounded-lg shadow-sm ${className}`}>{children}</div>
);

const CardHeader: React.FC<CardProps> = ({ children, className = "" }) => (
  <div className={`p-6 ${className}`}>{children}</div>
);

const CardTitle: React.FC<CardProps> = ({ children, className = "" }) => (
  <h3 className={`text-lg font-semibold tracking-tight ${className}`}>{children}</h3>
);

const CardContent: React.FC<CardProps> = ({ children, className = "" }) => (
  <div className={`p-6 pt-0 ${className}`}>{children}</div>
);

const TabsContext = React.createContext<{ activeTab: string; setActiveTab: (value: string) => void }>({ activeTab: '', setActiveTab: () => { } });

const Tabs: React.FC<TabsProps> = ({ children, value, onValueChange, className = "" }) => (
  <TabsContext.Provider value={{ activeTab: value, setActiveTab: onValueChange }}>
    <div className={className}>{children}</div>
  </TabsContext.Provider>
);

const TabsList: React.FC<TabsListProps> = ({ children, className = "" }) => (
  <div className={`flex items-center bg-gray-100 p-1 rounded-lg ${className}`}>{children}</div>
);

const TabsTrigger: React.FC<TabsTriggerProps> = ({ children, value }) => {
  const { activeTab, setActiveTab } = React.useContext(TabsContext);
  const isActive = activeTab === value;
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`flex-1 px-3 py-1.5 text-sm font-medium rounded-md transition-all ${isActive ? 'bg-white shadow-sm text-gray-900' : 'text-gray-500 hover:bg-gray-200'}`}
    >
      {children}
    </button>
  );
};

const TabsContent: React.FC<TabsContentProps> = ({ children, value, className = "" }) => {
  const { activeTab } = React.useContext(TabsContext);
  return activeTab === value ? <div className={className}>{children}</div> : null;
};

const Button: React.FC<ButtonProps> = ({ children, variant, size, onClick, className = "" }) => {
  const baseClasses = "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2";
  const variantClasses = variant === 'outline' ? 'border border-gray-300 bg-transparent hover:bg-gray-100' : 'bg-gray-900 text-white hover:bg-gray-800';
  const sizeClasses = size === 'sm' ? 'h-9 px-3' : 'h-10 px-4 py-2';
  return <button onClick={onClick} className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}>{children}</button>;
};

const Badge: React.FC<BadgeProps> = ({ children, variant, className = "" }) => {
  const variantClasses = variant === 'outline' ? 'border border-gray-300 text-gray-700' : 'bg-gray-100 text-gray-800';
  return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses} ${className}`}>{children}</span>;
};

const Progress: React.FC<ProgressProps> = ({ value, className = "" }) => (
  <div className={`h-2 w-full bg-gray-200 rounded-full overflow-hidden ${className}`}>
    <div className="h-full bg-blue-600 transition-all duration-300" style={{ width: `${value}%` }}></div>
  </div>
);


type IconProps = {
  children?: React.ReactNode;
  className?: string;
};

const Icon: React.FC<IconProps> = ({ children, className = "" }) => <div className={`inline-block ${className}`}>{children}</div>;
const Activity: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg></Icon>;
const Apple: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.9 4.9 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z"></path><path d="M10 2c1 .5 2 2 2 5"></path></svg></Icon>;
const Download: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></Icon>;
const Flame: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5Z"></path></svg></Icon>;
const Target: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg></Icon>;
const User: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg></Icon>;
const Utensils: React.FC<{ className?: string }> = ({ className = "" }) => <Icon className={className}><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"></path><path d="M7 2v20"></path><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3z"></path></svg></Icon>;


// --- CUSTOM HOOKS & PAGE COMPONENTS ---

// Remove the mock useAuth - we'll use the real one from hooks

// Dynamic imports for tab components
const DietPlan = React.lazy(() => import('./diet-plan'));
const WorkoutPlan = React.lazy(() => import('./workout-plan'));
const ProgressChart = React.lazy(() => import('./progress-chart'));


// --- THE DASHBOARD COMPONENT ---

type TodayStats = {
  calories_consumed: number;
  calories_target: number;
  calories_burned: number;
  workouts_completed: number;
  workouts_planned: number;
};

function Dashboard() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = React.useState("overview");
  const [todayStats, setTodayStats] = React.useState<TodayStats | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const fetchStats = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('/api/dashboard-stats', {
          method: 'GET',
          credentials: 'include'
        });
        
        const data = await response.json();
        
        if (!data.success) {
          throw new Error(data.message || "Failed to fetch dashboard stats");
        }
        setTodayStats(data.stats);
      } catch (err: any) {
        setError(err.message || "An error occurred");
        // Set fallback data if API fails
        setTodayStats({
          calories_consumed: 0,
          calories_target: 2000,
          calories_burned: 0,
          workouts_completed: 0,
          workouts_planned: 0,
        } as TodayStats);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchStats();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <span className="text-lg text-gray-500">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <span className="text-lg text-red-500">{error}</span>
      </div>
    );
  }

  if (!todayStats) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <span className="text-lg text-gray-500">No dashboard stats found.</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Welcome back, {user?.name || 'User'}!</h1>
              <p className="text-gray-600">Let's continue your fitness journey</p>
            </div>
            <div className="flex items-center gap-4">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export Plan
              </Button>
              <Button variant="outline" size="sm" onClick={logout}>
                <User className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="diet">Diet Plan</TabsTrigger>
            <TabsTrigger value="workout">Workout</TabsTrigger>
            <TabsTrigger value="progress">Progress</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Calories Today</CardTitle>
                  <Apple className="h-4 w-4 text-green-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{todayStats.calories_consumed}</div>
                  <p className="text-xs text-gray-500">of {todayStats.calories_target} target</p>
                  <Progress value={(todayStats.calories_consumed / todayStats.calories_target) * 100} className="mt-2" />
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Calories Burned</CardTitle>
                  <Flame className="h-4 w-4 text-red-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{todayStats.calories_burned}</div>
                  <p className="text-xs text-gray-500">from workouts</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Workouts</CardTitle>
                  <Activity className="h-4 w-4 text-blue-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {todayStats.workouts_completed}/{todayStats.workouts_planned}
                  </div>
                  <p className="text-xs text-gray-500">completed today</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Net Calories</CardTitle>
                  <Target className="h-4 w-4 text-purple-600" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{todayStats.calories_consumed - todayStats.calories_burned}</div>
                  <p className="text-xs text-gray-500">net intake</p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Utensils className="h-5 w-5" />
                    Today's Meal Plan
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between"><span className="text-sm">Breakfast</span><Badge variant="outline">450 cal</Badge></div>
                    <div className="flex items-center justify-between"><span className="text-sm">Lunch</span><Badge variant="outline">600 cal</Badge></div>
                    <div className="flex items-center justify-between"><span className="text-sm">Dinner</span><Badge variant="outline">400 cal</Badge></div>
                  </div>
                  <Button className="w-full mt-4" onClick={() => setActiveTab("diet")}>View Full Diet Plan</Button>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Today's Workout
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between"><span className="text-sm">Full Body Strength</span><Badge variant="outline">45 min</Badge></div>
                    <div className="flex items-center justify-between"><span className="text-sm">Estimated Burn</span><Badge variant="outline">{todayStats.calories_burned} cal</Badge></div>
                  </div>
                  <Button className="w-full mt-4" onClick={() => setActiveTab("workout")}>Start Workout</Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="diet">
            <React.Suspense fallback={<div className="flex items-center justify-center h-64"><span className="text-lg text-gray-500">Loading diet plan...</span></div>}>
              <DietPlan />
            </React.Suspense>
          </TabsContent>
          <TabsContent value="workout">
            <React.Suspense fallback={<div className="flex items-center justify-center h-64"><span className="text-lg text-gray-500">Loading workout plan...</span></div>}>
              <WorkoutPlan />
            </React.Suspense>
          </TabsContent>
          <TabsContent value="progress">
            <React.Suspense fallback={<div className="flex items-center justify-center h-64"><span className="text-lg text-gray-500">Loading progress chart...</span></div>}>
              <ProgressChart />
            </React.Suspense>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}


export default Dashboard;
