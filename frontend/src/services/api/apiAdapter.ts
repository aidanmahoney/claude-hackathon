// API Adapter Interface
// This defines the contract that any backend implementation must fulfill
// The actual implementation can be easily swapped out

import type { Course, MonitoredCourse, NotificationPreferences, EnrollmentSnapshot } from './types';

export interface ApiAdapter {
  // Course operations
  searchCourses(term: string, subject?: string, courseNumber?: string): Promise<Course[]>;
  getCourseDetails(term: string, subject: string, courseNumber: string): Promise<Course>;

  // Monitored courses operations
  getMonitoredCourses(): Promise<MonitoredCourse[]>;
  addMonitoredCourse(course: Omit<MonitoredCourse, 'id' | 'createdAt' | 'lastChecked'>): Promise<MonitoredCourse>;
  updateMonitoredCourse(id: string, updates: Partial<MonitoredCourse>): Promise<MonitoredCourse>;
  removeMonitoredCourse(id: string): Promise<void>;

  // Enrollment history
  getEnrollmentHistory(courseMonitorId: string): Promise<EnrollmentSnapshot[]>;

  // Notification preferences
  getNotificationPreferences(): Promise<NotificationPreferences>;
  updateNotificationPreferences(preferences: NotificationPreferences): Promise<NotificationPreferences>;

  // Testing
  testNotification(type: 'email' | 'sms' | 'webhook'): Promise<{ success: boolean; message: string }>;
}

// Configuration for the API adapter
export interface ApiConfig {
  baseUrl: string;
  timeout?: number;
  headers?: Record<string, string>;
}
