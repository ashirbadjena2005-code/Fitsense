"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Activity, Target, Utensils } from "lucide-react"
import LoginForm from "@/components/login-form"
import RegisterForm from "@/components/register-form"
import UserIntakeForm from "@/components/user-intake-form"
import Dashboard from "@/components/dashboard"
import { useAuth } from "@/hooks/use-auth"

export default function Home() {
  const [activeTab, setActiveTab] = useState("login")
  const { user, isAuthenticated, isLoading } = useAuth()

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (isAuthenticated && user) {
    if (!user.profileComplete) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
          <div className="container mx-auto max-w-4xl">
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Complete Your Profile</h1>
              <p className="text-gray-600">Help us personalize your diet and workout recommendations</p>
            </div>
            <UserIntakeForm />
          </div>
        </div>
      )
    }
    return <Dashboard />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered <span className="text-blue-600">Health & Fitness</span> Companion
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Get personalized diet plans, custom workout routines, and accurate calorie tracking powered by advanced
            machine learning algorithms.
          </p>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <Card className="border-0 shadow-lg">
              <CardHeader className="text-center">
                <Utensils className="h-12 w-12 text-green-600 mx-auto mb-4" />
                <CardTitle className="text-xl">Smart Diet Plans</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  AI-generated meal plans tailored to your goals, preferences, and dietary restrictions.
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardHeader className="text-center">
                <Activity className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                <CardTitle className="text-xl">Custom Workouts</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Personalized full-body workout routines with precise reps, sets, and timing.
                </p>
              </CardContent>
            </Card>

            <Card className="border-0 shadow-lg">
              <CardHeader className="text-center">
                <Target className="h-12 w-12 text-purple-600 mx-auto mb-4" />
                <CardTitle className="text-xl">Calorie Tracking</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Accurate calorie burn predictions and intake tracking with progress analytics.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Auth Section */}
        <div className="max-w-md mx-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Register</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <LoginForm />
            </TabsContent>

            <TabsContent value="register">
              <RegisterForm />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  )
}
