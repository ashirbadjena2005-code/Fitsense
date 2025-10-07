"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { TrendingUp, TrendingDown, Target, Award } from "lucide-react"

import { useEffect, useState } from "react"
export default function ProgressChart() {
const [progressData, setProgressData] = useState<any>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)

console.log('ProgressChart component rendered')

useEffect(() => {
  console.log('ProgressChart useEffect called')
  const fetchProgress = async () => {
    console.log('fetchProgress function called')
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/progress-data?days=7", {
        method: "GET",
        credentials: "include"
      })
      const data = await res.json()
      if (!data.success) throw new Error(data.message || "Failed to fetch progress data")
      // Transform backend data to frontend format with safe defaults
      setProgressData({
        weeklyStats: {
          caloriesConsumed: data.data.calories_consumed || [],
          caloriesBurned: data.data.calories_burned || [],
          weight: data.data.weights || [],
          workouts: data.data.workouts_completed || [],
        },
        // Achievements and goals can be calculated or fetched from backend if available
        achievements: [],
        goals: {
          currentWeight: data.data.weights && data.data.weights.length > 0 ? data.data.weights[data.data.weights.length - 1] : 0,
          targetWeight: 70.0, // Example, can be fetched from user profile
          startWeight: data.data.weights && data.data.weights.length > 0 ? data.data.weights[0] : 0,
          targetDate: "2024-06-01",
          weeklyTarget: 0.5,
        },
      })
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  fetchProgress()
}, [])

const weightLossProgress = progressData && progressData.goals ?
  ((progressData.goals.startWeight - progressData.goals.currentWeight) /
    (progressData.goals.startWeight - progressData.goals.targetWeight)) *
  100 : 0

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

if (loading) {
  return (
    <div className="flex items-center justify-center h-64">
      <span className="text-lg text-gray-500">Loading progress data...</span>
    </div>
  )
}
if (error) {
  return (
    <div className="flex items-center justify-center h-64">
      <span className="text-lg text-red-500">{error}</span>
    </div>
  )
}

if (!progressData) {
  return (
    <div className="flex items-center justify-center h-64">
      <span className="text-lg text-gray-500">No progress data available. Start logging your activities to see your progress!</span>
    </div>
  )
}

return (
  <div className="space-y-6">
    {/* Progress Overview */}
    <div className="grid md:grid-cols-3 gap-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Weight Progress</CardTitle>
          <TrendingDown className="h-4 w-4 text-green-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{progressData.goals.currentWeight} kg</div>
          <p className="text-xs text-muted-foreground">
            -{(progressData.goals.startWeight - progressData.goals.currentWeight).toFixed(1)}kg from start
          </p>
          <div className="mt-2 h-2 bg-gray-200 rounded-full">
            <div
              className="h-2 bg-green-600 rounded-full"
              style={{ width: `${Math.min(weightLossProgress, 100)}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Weekly Average</CardTitle>
          <Target className="h-4 w-4 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {progressData.weeklyStats.caloriesConsumed.length > 0 
              ? Math.round(progressData.weeklyStats.caloriesConsumed.reduce((a: number, b: number) => a + b, 0) / 7)
              : 0}
          </div>
          <p className="text-xs text-muted-foreground">calories per day</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Workout Streak</CardTitle>
          <Award className="h-4 w-4 text-purple-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{progressData.weeklyStats.workouts.filter((w: number) => w > 0).length}</div>
          <p className="text-xs text-muted-foreground">days in a row</p>
        </CardContent>
      </Card>
    </div>

    <Tabs defaultValue="weekly" className="space-y-4">
      <TabsList>
        <TabsTrigger value="weekly">Weekly View</TabsTrigger>
        <TabsTrigger value="achievements">Achievements</TabsTrigger>
        <TabsTrigger value="goals">Goals</TabsTrigger>
      </TabsList>

      <TabsContent value="weekly" className="space-y-4">
        {/* Weekly Charts */}
        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardHeader>
              <CardTitle>Daily Calories</CardTitle>
              <CardDescription>Consumed vs Burned this week</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {days.map((day, index) => (
                  <div key={day} className="flex items-center gap-4">
                    <div className="w-8 text-sm font-medium">{day}</div>
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span>Consumed: {progressData.weeklyStats.caloriesConsumed[index]}</span>
                        <span>Burned: {progressData.weeklyStats.caloriesBurned[index]}</span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 rounded-full"
                          style={{
                            width: `${(progressData.weeklyStats.caloriesConsumed[index] / 2500) * 100}%`,
                          }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Weight Trend</CardTitle>
              <CardDescription>Daily weight measurements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {days.map((day, index) => (
                  <div key={day} className="flex items-center justify-between">
                    <div className="text-sm font-medium">{day}</div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm">{progressData.weeklyStats.weight[index]} kg</span>
                      {index > 0 && (
                        <Badge
                          variant={
                            progressData.weeklyStats.weight[index] < progressData.weeklyStats.weight[index - 1]
                              ? "default"
                              : "secondary"
                          }
                          className="text-xs"
                        >
                          {progressData.weeklyStats.weight[index] < progressData.weeklyStats.weight[index - 1] ? (
                            <TrendingDown className="h-3 w-3" />
                          ) : (
                            <TrendingUp className="h-3 w-3" />
                          )}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      <TabsContent value="achievements" className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          {progressData.achievements.map((achievement: any, index: number) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl">{achievement.icon}</span>
                  {achievement.title}
                </CardTitle>
                <CardDescription>{achievement.date}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600">{achievement.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </TabsContent>

      <TabsContent value="goals" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Weight Loss Goal</CardTitle>
            <CardDescription>Track your progress towards your target weight</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-600">{progressData.goals.startWeight} kg</div>
                <div className="text-sm text-gray-500">Starting Weight</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{progressData.goals.currentWeight} kg</div>
                <div className="text-sm text-gray-500">Current Weight</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{progressData.goals.targetWeight} kg</div>
                <div className="text-sm text-gray-500">Target Weight</div>
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Progress</span>
                <span>{weightLossProgress.toFixed(1)}% complete</span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full">
                <div
                  className="h-3 bg-gradient-to-r from-blue-500 to-green-500 rounded-full transition-all duration-300"
                  style={{ width: `${Math.min(weightLossProgress, 100)}%` }}
                />
              </div>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-600">
                {(progressData.goals.currentWeight - progressData.goals.targetWeight).toFixed(1)} kg to go
              </p>
              <p className="text-xs text-gray-500 mt-1">Target date: {progressData.goals.targetDate}</p>
            </div>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  </div>
)
}
