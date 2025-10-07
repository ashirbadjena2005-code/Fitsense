"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Button } from "./ui/button"
import { Progress } from "./ui/progress"
import { Activity, FlameIcon as Fire, Play, CheckCircle, Timer, Settings, X, Dumbbell, Clock, Target, Zap } from "lucide-react"

export default function WorkoutPlan() {
  const [workoutPlan, setWorkoutPlan] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentExercise, setCurrentExercise] = useState(0)
  const [isWorkoutActive, setIsWorkoutActive] = useState(false)
  const [completedExercises, setCompletedExercises] = useState<number[]>([])
  const [showCustomizeModal, setShowCustomizeModal] = useState(false)
  const [customizing, setCustomizing] = useState(false)

  // Customization options
  const [customization, setCustomization] = useState({
    duration: 30,
    difficulty: 'intermediate',
    focusAreas: [] as string[],
    equipment: [] as string[],
    workoutType: 'full_body'
  })

  const focusAreaOptions = [
    'Upper Body', 'Lower Body', 'Core', 'Cardio', 'Strength', 'Flexibility', 'HIIT', 'Yoga'
  ]

  const equipmentOptions = [
    'No Equipment', 'Dumbbells', 'Resistance Bands', 'Yoga Mat', 'Pull-up Bar', 'Kettlebell', 'Treadmill', 'Weights'
  ]

  const difficultyOptions = [
    { value: 'beginner', label: 'Beginner', color: 'text-green-600' },
    { value: 'intermediate', label: 'Intermediate', color: 'text-yellow-600' },
    { value: 'advanced', label: 'Advanced', color: 'text-red-600' }
  ]

  const workoutTypeOptions = [
    { value: 'full_body', label: 'Full Body', icon: '🏋️' },
    { value: 'upper_body', label: 'Upper Body', icon: '💪' },
    { value: 'lower_body', label: 'Lower Body', icon: '🦵' },
    { value: 'cardio', label: 'Cardio', icon: '❤️' },
    { value: 'hiit', label: 'HIIT', icon: '⚡' },
    { value: 'yoga', label: 'Yoga', icon: '🧘' }
  ]

  console.log('WorkoutPlan component rendered')

  useEffect(() => {
    console.log('WorkoutPlan useEffect called')
    const fetchWorkoutPlan = async () => {
      console.log('fetchWorkoutPlan function called')
      setLoading(true)
      setError(null)
      try {
        const res = await fetch("/api/workout-plan", {
          method: "GET",
          credentials: "include"
        })
        const data = await res.json()
        if (!data.success) throw new Error(data.message || "Failed to fetch workout plan")
        setWorkoutPlan({
          name: data.workout.name,
          duration: data.workout.total_duration,
          estimatedCalories: data.workout.total_calories,
          difficulty: "Intermediate", // You can adjust this if backend provides
          exercises: data.workout.exercises,
        })
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    fetchWorkoutPlan()
  }, [])

  const totalExercises = workoutPlan?.exercises?.length || 0
  const progressPercentage = totalExercises ? (completedExercises.length / totalExercises) * 100 : 0

  const completeExercise = (index: number) => {
    if (!completedExercises.includes(index)) {
      setCompletedExercises([...completedExercises, index])
    }
  }

  const startWorkout = () => {
    setIsWorkoutActive(true)
    setCurrentExercise(0)
  }

  const handleCustomizeWorkout = () => {
    setShowCustomizeModal(true)
  }

  const handleCustomizationChange = (key: string, value: any) => {
    setCustomization(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleFocusAreaToggle = (area: string) => {
    setCustomization(prev => ({
      ...prev,
      focusAreas: prev.focusAreas.includes(area)
        ? prev.focusAreas.filter(a => a !== area)
        : [...prev.focusAreas, area]
    }))
  }

  const handleEquipmentToggle = (equipment: string) => {
    setCustomization(prev => ({
      ...prev,
      equipment: prev.equipment.includes(equipment)
        ? prev.equipment.filter(e => e !== equipment)
        : [...prev.equipment, equipment]
    }))
  }

  const generateCustomWorkout = async () => {
    setCustomizing(true)
    try {
      const res = await fetch("/api/workout-plan", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          duration: customization.duration,
          difficulty: customization.difficulty,
          focus_areas: customization.focusAreas,
          equipment: customization.equipment,
          workout_type: customization.workoutType
        })
      })
      
      const data = await res.json()
      if (!data.success) throw new Error(data.message || "Failed to generate custom workout")
      
      setWorkoutPlan({
        name: data.workout.name,
        duration: data.workout.total_duration,
        estimatedCalories: data.workout.total_calories,
        difficulty: customization.difficulty,
        exercises: data.workout.exercises,
      })
      
      setShowCustomizeModal(false)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setCustomizing(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <span className="text-lg text-gray-500">Loading your workout plan...</span>
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
  if (!workoutPlan) {
    return (
      <div className="flex items-center justify-center h-64">
        <span className="text-lg text-gray-500">No workout plan found. Complete your profile to generate one.</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Workout Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            {workoutPlan.name}
          </CardTitle>
          <CardDescription>AI-customized workout based on your fitness level and available time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{workoutPlan.duration}</div>
              <div className="text-sm text-gray-600">Minutes</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">{workoutPlan.estimatedCalories}</div>
              <div className="text-sm text-gray-600">Calories</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{totalExercises}</div>
              <div className="text-sm text-gray-600">Exercises</div>
            </div>
            <div className="text-center">
              <Badge variant="outline" className="text-lg px-3 py-1">
                {workoutPlan.difficulty}
              </Badge>
            </div>
          </div>

          {isWorkoutActive && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Workout Progress</span>
                <span className="text-sm text-gray-600">
                  {completedExercises.length}/{totalExercises} completed
                </span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>
          )}

          <div className="flex gap-4">
            {!isWorkoutActive ? (
              <Button onClick={startWorkout} className="flex-1">
                <Play className="h-4 w-4 mr-2" />
                Start Workout
              </Button>
            ) : (
              <Button variant="outline" onClick={() => setIsWorkoutActive(false)} className="flex-1">
                End Workout
              </Button>
            )}
            <Button variant="outline" onClick={handleCustomizeWorkout} className="flex-1">
              <Settings className="h-4 w-4 mr-2" />
              Customize Workout
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Exercise List */}
      <div className="space-y-4">
        {workoutPlan.exercises.map((exercise: any, index: number) => (
          <Card
            key={index}
            className={`${isWorkoutActive && currentExercise === index
                ? "ring-2 ring-blue-500 bg-blue-50"
                : completedExercises.includes(index)
                  ? "bg-green-50 border-green-200"
                  : ""
              }`}
          >
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  {completedExercises.includes(index) ? (
                    <CheckCircle className="h-5 w-5 text-green-600" />
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-gray-300 flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                  )}
                  {exercise.name}
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="flex items-center gap-1">
                    <Timer className="h-3 w-3" />
                    {exercise.duration} min
                  </Badge>
                  <Badge variant="outline" className="flex items-center gap-1">
                    <Fire className="h-3 w-3" />
                    {exercise.calories} cal
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-4">
                  <div className="text-sm">
                    <span className="font-medium">Sets:</span> {exercise.sets}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Reps:</span> {exercise.reps}
                  </div>
                </div>

                <div className="text-sm text-gray-600">
                  <span className="font-medium">Instructions:</span> {exercise.instructions}
                </div>

                <div className="flex flex-wrap gap-1">
                  {exercise.muscleGroups?.map((muscle: any, muscleIndex: number) => (
                    <Badge key={muscleIndex} variant="secondary" className="text-xs">
                      {muscle}
                    </Badge>
                  ))}
                </div>

                {isWorkoutActive && (
                  <div className="flex gap-2 pt-2">
                    <Button
                      size="sm"
                      onClick={() => completeExercise(index)}
                      disabled={completedExercises.includes(index)}
                    >
                      {completedExercises.includes(index) ? "Completed" : "Mark Complete"}
                    </Button>
                    <Button size="sm" variant="outline" onClick={() => setCurrentExercise(index)}>
                      Focus
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Customization Modal */}
      {showCustomizeModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                  <Settings className="h-6 w-6" />
                  Customize Your Workout
                </h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowCustomizeModal(false)}
                  className="p-2"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              <div className="space-y-6">
                {/* Duration */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Clock className="h-4 w-4 inline mr-2" />
                    Workout Duration (minutes)
                  </label>
                  <div className="flex items-center space-x-4">
                    <input
                      type="range"
                      min="10"
                      max="120"
                      step="5"
                      value={customization.duration}
                      onChange={(e) => handleCustomizationChange('duration', parseInt(e.target.value))}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    />
                    <span className="text-lg font-semibold text-blue-600 min-w-[3rem]">
                      {customization.duration} min
                    </span>
                  </div>
                </div>

                {/* Difficulty */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Target className="h-4 w-4 inline mr-2" />
                    Difficulty Level
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    {difficultyOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => handleCustomizationChange('difficulty', option.value)}
                        className={`p-3 rounded-lg border-2 transition-all ${
                          customization.difficulty === option.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className={`font-medium ${option.color}`}>{option.label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Workout Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Activity className="h-4 w-4 inline mr-2" />
                    Workout Type
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {workoutTypeOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => handleCustomizationChange('workoutType', option.value)}
                        className={`p-3 rounded-lg border-2 transition-all ${
                          customization.workoutType === option.value
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="text-2xl mb-1">{option.icon}</div>
                        <div className="font-medium text-sm">{option.label}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Focus Areas */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Zap className="h-4 w-4 inline mr-2" />
                    Focus Areas (Select multiple)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {focusAreaOptions.map((area) => (
                      <button
                        key={area}
                        onClick={() => handleFocusAreaToggle(area)}
                        className={`p-2 rounded-lg border text-sm transition-all ${
                          customization.focusAreas.includes(area)
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {area}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Equipment */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    <Dumbbell className="h-4 w-4 inline mr-2" />
                    Available Equipment (Select multiple)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                    {equipmentOptions.map((equipment) => (
                      <button
                        key={equipment}
                        onClick={() => handleEquipmentToggle(equipment)}
                        className={`p-2 rounded-lg border text-sm transition-all ${
                          customization.equipment.includes(equipment)
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {equipment}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 mt-8 pt-6 border-t">
                <Button
                  variant="outline"
                  onClick={() => setShowCustomizeModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  onClick={generateCustomWorkout}
                  disabled={customizing}
                  className="flex-1"
                >
                  {customizing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <Zap className="h-4 w-4 mr-2" />
                      Generate Custom Workout
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
