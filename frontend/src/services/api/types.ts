// Core types for the application
// These can be adjusted to match backend API responses

export interface Course {
  id: string;
  term: string;
  subject: string;
  courseNumber: string;
  title?: string;
  credits?: number;
  sections: CourseSection[];
}

export interface CourseSection {
  sectionId: string;
  totalSeats: number;
  openSeats: number;
  enrolledSeats: number;
  waitlistTotal?: number;
  waitlistOpen?: number;
  status: EnrollmentStatus;
  instructor?: string;
  schedule?: string;
  location?: string;
}

export type EnrollmentStatus = 'OPEN' | 'CLOSED' | 'WAITLIST' | 'CANCELLED';

export interface MonitoredCourse {
  id: string;
  term: string;
  subject: string;
  courseNumber: string;
  sections: string[];
  notifyOnOpen: boolean;
  notifyOnWaitlist: boolean;
  checkInterval: number;
  active: boolean;
  lastChecked?: Date;
  createdAt: Date;
}

export interface EnrollmentSnapshot {
  id: string;
  courseMonitorId: string;
  totalSeats: number;
  openSeats: number;
  enrolledSeats: number;
  waitlistTotal?: number;
  waitlistOpen?: number;
  status: EnrollmentStatus;
  timestamp: Date;
}

export interface NotificationPreferences {
  email?: {
    enabled: boolean;
    address: string;
  };
  sms?: {
    enabled: boolean;
    phoneNumber: string;
  };
  webhook?: {
    enabled: boolean;
    url: string;
  };
}

export interface User {
  id: string;
  email: string;
  name?: string;
  notificationPreferences: NotificationPreferences;
}
