"use client"


import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Separator } from "./ui/separator"
import { Apple, Clock, Utensils } from "lucide-react"
import { useAuth } from "../hooks/use-auth"

export default function DietPlan() {
const [dietPlan, setDietPlan] = useState<any>(null)
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
const { user } = useAuth()

console.log('DietPlan component rendered, user:', user)

useEffect(() => {
  console.log('DietPlan useEffect called, user:', user)
  const fetchDietPlan = async () => {
    console.log('fetchDietPlan function called')
    setLoading(true)
    setError(null)
    try {
      const res = await fetch("/api/diet-plan", {
        method: "GET",
        credentials: "include"
      })
      const data = await res.json()
      console.log("Diet plan API response:", data) // Debug log
      if (!data.success) throw new Error(data.message || "Failed to fetch diet plan")
      // Transform backend data to frontend format
      const mealsArr = Object.entries(data.meals).map(([type, items]: any, idx) => {
        // Estimate time and calories from items if not present
        const calories = items.reduce((sum: number, item: any) => sum + item.calories, 0)
        return {
          type,
          time: idx === 0 ? "8:00 AM" : idx === 1 ? "1:00 PM" : "7:00 PM",
          calories,
          items,
        }
      })
      const transformedData = {
        totalCalories: data.totals.calories,
        macros: {
          protein: data.totals.protein,
          carbs: data.totals.carbs,
          fat: data.totals.fat,
        },
        meals: mealsArr,
      }
      console.log("Transformed diet plan data:", transformedData) // Debug log
      setDietPlan(transformedData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }
  if (user) fetchDietPlan()
}, [user])

if (loading) {
  return (
    <div className="flex items-center justify-center h-64">
      <span className="text-lg text-gray-500">Loading your diet plan...</span>
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
if (!dietPlan) {
  return (
    <div className="flex items-center justify-center h-64">
      <span className="text-lg text-gray-500">No diet plan found. Complete your profile to generate one.</span>
    </div>
  )
}

return (
  <div className="space-y-6">
    {/* Summary Card */}
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Apple className="h-5 w-5" />
          Your Personalized Diet Plan
        </CardTitle>
        <CardDescription>AI-generated meal plan based on your goals and preferences</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{dietPlan.totalCalories}</div>
            <div className="text-sm text-gray-600">Total Calories</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{dietPlan.macros.protein}g</div>
            <div className="text-sm text-gray-600">Protein</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{dietPlan.macros.carbs}g</div>
            <div className="text-sm text-gray-600">Carbs</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{dietPlan.macros.fat}g</div>
            <div className="text-sm text-gray-600">Fat</div>
          </div>
        </div>
      </CardContent>
    </Card>

    {/* Meal Cards */}
    <div className="space-y-4">
      {dietPlan.meals.map((meal: any, index: number) => (
        <Card key={index}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <Utensils className="h-4 w-4" />
                {meal.type}
              </CardTitle>
              <div className="flex items-center gap-4">
                <Badge variant="outline" className="flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {meal.time}
                </Badge>
                <Badge className="bg-blue-100 text-blue-800">{meal.calories} cal</Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {meal.items.map((item: any, itemIndex: number) => (
                <div key={itemIndex}>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{item.name}</div>
                      <div className="text-sm text-gray-600">
                        P: {item.protein}g | C: {item.carbs}g | F: {item.fat}g
                      </div>
                    </div>
                    <Badge variant="outline">{item.calories} cal</Badge>
                  </div>
                  {itemIndex < meal.items.length - 1 && <Separator className="mt-3" />}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>

    <div className="flex gap-4">
      <Button className="flex-1">
        <Apple className="h-4 w-4 mr-2" />
        Log Food Intake
      </Button>
      <Button variant="outline" className="flex-1 bg-transparent">
        Customize Plan
      </Button>
    </div>
  </div>
)
}
