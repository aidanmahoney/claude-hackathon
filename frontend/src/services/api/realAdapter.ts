// Real API Adapter
// This will connect to your actual backend API
// Adjust the endpoints and data transformations to match your backend

import axios, { type AxiosInstance } from 'axios';
import type { ApiAdapter, ApiConfig } from './apiAdapter';
import type { Course, MonitoredCourse, NotificationPreferences, EnrollmentSnapshot } from './types';

export class RealApiAdapter implements ApiAdapter {
  private client: AxiosInstance;

  constructor(config: ApiConfig) {
    this.client = axios.create({
      baseURL: config.baseUrl,
      timeout: config.timeout || 10000,
      headers: {
        'Content-Type': 'application/json',
        ...config.headers
      }
    });

    // Add request interceptor for auth tokens if needed
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token from localStorage or other source
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle common errors
        if (error.response?.status === 401) {
          // Handle unauthorized
          console.error('Unauthorized access');
        }
        return Promise.reject(error);
      }
    );
  }

  async searchCourses(term: string, subject?: string, courseNumber?: string): Promise<Course[]> {
    // ADJUST THIS ENDPOINT to match your backend
    const response = await this.client.get('/courses/search', {
      params: { term, subject, courseNumber }
    });

    // ADJUST THIS TRANSFORMATION to match your backend response format
    return this.transformCoursesResponse(response.data);
  }

  async getCourseDetails(term: string, subject: string, courseNumber: string): Promise<Course> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.get(`/courses/${term}/${subject}/${courseNumber}`);

    // ADJUST THIS TRANSFORMATION
    return this.transformCourseResponse(response.data);
  }

  async getMonitoredCourses(): Promise<MonitoredCourse[]> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.get('/monitors');

    // ADJUST THIS TRANSFORMATION
    return this.transformMonitoredCoursesResponse(response.data);
  }

  async addMonitoredCourse(course: Omit<MonitoredCourse, 'id' | 'createdAt' | 'lastChecked'>): Promise<MonitoredCourse> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.post('/monitors', course);

    // ADJUST THIS TRANSFORMATION
    return this.transformMonitoredCourseResponse(response.data);
  }

  async updateMonitoredCourse(id: string, updates: Partial<MonitoredCourse>): Promise<MonitoredCourse> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.patch(`/monitors/${id}`, updates);

    // ADJUST THIS TRANSFORMATION
    return this.transformMonitoredCourseResponse(response.data);
  }

  async removeMonitoredCourse(id: string): Promise<void> {
    // ADJUST THIS ENDPOINT
    await this.client.delete(`/monitors/${id}`);
  }

  async getEnrollmentHistory(courseMonitorId: string): Promise<EnrollmentSnapshot[]> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.get(`/monitors/${courseMonitorId}/history`);

    // ADJUST THIS TRANSFORMATION
    return this.transformEnrollmentHistoryResponse(response.data);
  }

  async getNotificationPreferences(): Promise<NotificationPreferences> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.get('/preferences/notifications');

    // ADJUST THIS TRANSFORMATION
    return response.data;
  }

  async updateNotificationPreferences(preferences: NotificationPreferences): Promise<NotificationPreferences> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.put('/preferences/notifications', preferences);

    // ADJUST THIS TRANSFORMATION
    return response.data;
  }

  async testNotification(type: 'email' | 'sms' | 'webhook'): Promise<{ success: boolean; message: string }> {
    // ADJUST THIS ENDPOINT
    const response = await this.client.post('/notifications/test', { type });

    // ADJUST THIS TRANSFORMATION
    return response.data;
  }

  // ==========================================
  // TRANSFORMATION METHODS
  // Adjust these to match your backend's response format
  // ==========================================

  private transformCoursesResponse(data: any): Course[] {
    // Example transformation - adjust to your backend format
    if (Array.isArray(data)) {
      return data.map(item => this.transformCourseResponse(item));
    }
    return data.courses || data.data || data;
  }

  private transformCourseResponse(data: any): Course {
    // Example transformation - adjust to your backend format
    return {
      id: data.id || data._id || `${data.subject}-${data.courseNumber}`,
      term: data.term,
      subject: data.subject,
      courseNumber: data.courseNumber || data.course_number,
      title: data.title || data.courseName,
      credits: data.credits,
      sections: (data.sections || []).map((section: any) => ({
        sectionId: section.sectionId || section.section_id || section.id,
        totalSeats: section.totalSeats || section.total_seats,
        openSeats: section.openSeats || section.open_seats,
        enrolledSeats: section.enrolledSeats || section.enrolled_seats,
        waitlistTotal: section.waitlistTotal || section.waitlist_total,
        waitlistOpen: section.waitlistOpen || section.waitlist_open,
        status: section.status || section.enrollmentStatus,
        instructor: section.instructor,
        schedule: section.schedule || section.time,
        location: section.location || section.room
      }))
    };
  }

  private transformMonitoredCoursesResponse(data: any): MonitoredCourse[] {
    if (Array.isArray(data)) {
      return data.map(item => this.transformMonitoredCourseResponse(item));
    }
    return data.monitors || data.data || data;
  }

  private transformMonitoredCourseResponse(data: any): MonitoredCourse {
    return {
      id: data.id || data._id,
      term: data.term,
      subject: data.subject,
      courseNumber: data.courseNumber || data.course_number,
      sections: data.sections || [],
      notifyOnOpen: data.notifyOnOpen ?? data.notify_on_open ?? true,
      notifyOnWaitlist: data.notifyOnWaitlist ?? data.notify_on_waitlist ?? false,
      checkInterval: data.checkInterval || data.check_interval || 300000,
      active: data.active ?? true,
      lastChecked: data.lastChecked ? new Date(data.lastChecked) : undefined,
      createdAt: new Date(data.createdAt || data.created_at)
    };
  }

  private transformEnrollmentHistoryResponse(data: any): EnrollmentSnapshot[] {
    if (Array.isArray(data)) {
      return data.map(item => ({
        id: item.id || item._id,
        courseMonitorId: item.courseMonitorId || item.course_monitor_id,
        totalSeats: item.totalSeats || item.total_seats,
        openSeats: item.openSeats || item.open_seats,
        enrolledSeats: item.enrolledSeats || item.enrolled_seats,
        waitlistTotal: item.waitlistTotal || item.waitlist_total,
        waitlistOpen: item.waitlistOpen || item.waitlist_open,
        status: item.status,
        timestamp: new Date(item.timestamp)
      }));
    }
    return data.history || data.snapshots || data.data || data;
  }
}
