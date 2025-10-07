"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

interface User {
  id: number
  email: string
  name: string
  profileComplete: boolean
  profile?: any
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  register: (name: string, email: string, password: string) => Promise<boolean>
  logout: () => Promise<void>
  updateProfile: (profileData: any) => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Check if user is already logged in on app start
  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      console.log('Checking authentication status...')
      const response = await fetch('/api/health', {
        credentials: 'include'
      })
      console.log('Health check response:', response.status)
      if (response.ok) {
        // Try to get user profile to check if logged in
        const profileResponse = await fetch('/api/profile', {
          method: 'GET',
          credentials: 'include'
        })
        console.log('Profile check response:', profileResponse.status)
        if (profileResponse.ok) {
          const profileData = await profileResponse.json()
          console.log('Profile data received:', profileData)
          if (profileData.success && profileData.user) {
            // Set user with profile completion status
            const userData = {
              ...profileData.user,
              profileComplete: profileData.user.profile_complete || false
            }
            console.log('Setting user data:', userData)
            setUser(userData)
          }
        } else {
          console.log('Profile check failed:', profileResponse.status)
        }
      } else {
        console.log('Health check failed:', response.status)
      }
    } catch (error) {
      console.log('No active session:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      })

      const data = await response.json()
      
      if (data.success) {
        setUser({
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          profileComplete: data.user.profile_complete,
        })
        return true
      } else {
        alert(data.message || 'Login failed')
        return false
      }
    } catch (error) {
      console.error('Login error:', error)
      alert('Login failed. Please try again.')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (name: string, email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ name, email, password }),
      })

      const data = await response.json()
      
      if (data.success) {
        setUser({
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          profileComplete: false,
        })
        return true
      } else {
        alert(data.message || 'Registration failed')
        return false
      }
    } catch (error) {
      console.error('Registration error:', error)
      alert('Registration failed. Please try again.')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async (): Promise<void> => {
    try {
      await fetch('/api/logout', {
        method: 'POST',
        credentials: 'include',
      })
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
    }
  }

  const updateProfile = async (profileData: any): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(profileData),
      })

      const data = await response.json()
      
      if (data.success) {
        if (user) {
          setUser({
            ...user,
            profileComplete: true,
            profile: profileData,
          })
        }
        return true
      } else {
        alert(data.message || 'Profile update failed')
        return false
      }
    } catch (error) {
      console.error('Profile update error:', error)
      alert('Profile update failed. Please try again.')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
