"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useAuth } from "@/hooks/use-auth"
import { Loader2 } from "lucide-react"

export default function UserIntakeForm() {
  const [formData, setFormData] = useState({
    age: "",
    gender: "",
    height: "",
    weight: "",
    goal: "",
    dietPreference: "",
    activityLevel: "",
    workoutTime: "",
  })
  const { updateProfile, isLoading } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validate required fields
    const requiredFields = ['age', 'gender', 'height', 'weight', 'goal', 'dietPreference', 'activityLevel', 'workoutTime']
    const missingFields = requiredFields.filter(field => !formData[field as keyof typeof formData])
    
    if (missingFields.length > 0) {
      alert(`Please fill in all required fields: ${missingFields.join(', ')}`)
      return
    }
    
    // Transform form data to match backend expectations
    const profileData = {
      age: parseInt(formData.age),
      gender: formData.gender,
      height: parseFloat(formData.height),
      weight: parseFloat(formData.weight),
      goal: formData.goal,
      diet_preference: formData.dietPreference,
      activity_level: formData.activityLevel,
      workout_time: formData.workoutTime,
    }
    
    await updateProfile(profileData)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Personal Information</CardTitle>
        <CardDescription>Tell us about yourself so we can create the perfect plan for you</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                name="age"
                type="number"
                placeholder="Enter your age"
                value={formData.age}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="space-y-2">
              <Label>Gender</Label>
              <RadioGroup value={formData.gender} onValueChange={(value) => handleSelectChange("gender", value)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="male" id="male" />
                  <Label htmlFor="male">Male</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="female" id="female" />
                  <Label htmlFor="female">Female</Label>
                </div>
              </RadioGroup>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="height">Height (cm)</Label>
              <Input
                id="height"
                name="height"
                type="number"
                placeholder="Enter your height"
                value={formData.height}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="weight">Weight (kg)</Label>
              <Input
                id="weight"
                name="weight"
                type="number"
                placeholder="Enter your weight"
                value={formData.weight}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Fitness Goal</Label>
            <Select onValueChange={(value) => handleSelectChange("goal", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select your primary goal" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="weight-loss">Weight Loss</SelectItem>
                <SelectItem value="maintenance">Weight Maintenance</SelectItem>
                <SelectItem value="muscle-gain">Muscle Gain</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Diet Preference</Label>
            <Select onValueChange={(value) => handleSelectChange("dietPreference", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select your diet preference" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="non-vegan">Non-Vegan</SelectItem>
                <SelectItem value="vegan">Vegan</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Activity Level</Label>
            <Select onValueChange={(value) => handleSelectChange("activityLevel", value)}>
              <SelectTrigger>
                <SelectValue placeholder="Select your activity level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="sedentary">Sedentary (Little to no exercise)</SelectItem>
                <SelectItem value="light">Light (Light exercise 1-3 days/week)</SelectItem>
                <SelectItem value="moderate">Moderate (Moderate exercise 3-5 days/week)</SelectItem>
                <SelectItem value="intense">Intense (Heavy exercise 6-7 days/week)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Available Workout Time (minutes/day)</Label>
            <Select onValueChange={(value) => handleSelectChange("workoutTime", value)}>
              <SelectTrigger>
                <SelectValue placeholder="How much time can you dedicate?" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="15-30">15-30 minutes</SelectItem>
                <SelectItem value="30-45">30-45 minutes</SelectItem>
                <SelectItem value="45-60">45-60 minutes</SelectItem>
                <SelectItem value="60+">60+ minutes</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Generate My Plan
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
