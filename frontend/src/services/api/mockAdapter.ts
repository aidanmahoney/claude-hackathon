// Mock API Adapter for development
// This can be used while the backend is being developed
// Replace with real adapter when backend is ready

import type { ApiAdapter } from './apiAdapter';
import type { Course, MonitoredCourse, NotificationPreferences, EnrollmentSnapshot, EnrollmentStatus } from './types';

export class MockApiAdapter implements ApiAdapter {
  private mockMonitoredCourses: MonitoredCourse[] = [];
  private mockPreferences: NotificationPreferences = {
    email: { enabled: false, address: '' },
    sms: { enabled: false, phoneNumber: '' },
    webhook: { enabled: false, url: '' }
  };

  async searchCourses(term: string, subject?: string, courseNumber?: string): Promise<Course[]> {
    // Simulate API delay
    await this.delay(500);

    // Return mock data
    return [
      {
        id: '1',
        term,
        subject: subject || 'COMP SCI',
        courseNumber: courseNumber || '400',
        title: 'Programming III',
        credits: 3,
        sections: [
          {
            sectionId: '001',
            totalSeats: 30,
            openSeats: 2,
            enrolledSeats: 28,
            waitlistTotal: 10,
            waitlistOpen: 3,
            status: 'OPEN' as EnrollmentStatus,
            instructor: 'Prof. Smith',
            schedule: 'MWF 10:00-10:50',
            location: 'CS 1240'
          },
          {
            sectionId: '002',
            totalSeats: 30,
            openSeats: 0,
            enrolledSeats: 30,
            waitlistTotal: 10,
            waitlistOpen: 0,
            status: 'CLOSED' as EnrollmentStatus,
            instructor: 'Prof. Johnson',
            schedule: 'TR 11:00-12:15',
            location: 'CS 1350'
          }
        ]
      }
    ];
  }

  async getCourseDetails(term: string, subject: string, courseNumber: string): Promise<Course> {
    await this.delay(300);

    return {
      id: '1',
      term,
      subject,
      courseNumber,
      title: 'Programming III',
      credits: 3,
      sections: [
        {
          sectionId: '001',
          totalSeats: 30,
          openSeats: 2,
          enrolledSeats: 28,
          waitlistTotal: 10,
          waitlistOpen: 3,
          status: 'OPEN' as EnrollmentStatus,
          instructor: 'Prof. Smith',
          schedule: 'MWF 10:00-10:50',
          location: 'CS 1240'
        }
      ]
    };
  }

  async getMonitoredCourses(): Promise<MonitoredCourse[]> {
    await this.delay(300);
    return this.mockMonitoredCourses;
  }

  async addMonitoredCourse(course: Omit<MonitoredCourse, 'id' | 'createdAt' | 'lastChecked'>): Promise<MonitoredCourse> {
    await this.delay(300);

    const newCourse: MonitoredCourse = {
      ...course,
      id: String(Date.now()),
      createdAt: new Date(),
      lastChecked: undefined
    };

    this.mockMonitoredCourses.push(newCourse);
    return newCourse;
  }

  async updateMonitoredCourse(id: string, updates: Partial<MonitoredCourse>): Promise<MonitoredCourse> {
    await this.delay(300);

    const index = this.mockMonitoredCourses.findIndex(c => c.id === id);
    if (index === -1) throw new Error('Course not found');

    this.mockMonitoredCourses[index] = { ...this.mockMonitoredCourses[index], ...updates };
    return this.mockMonitoredCourses[index];
  }

  async removeMonitoredCourse(id: string): Promise<void> {
    await this.delay(300);

    const index = this.mockMonitoredCourses.findIndex(c => c.id === id);
    if (index === -1) throw new Error('Course not found');

    this.mockMonitoredCourses.splice(index, 1);
  }

  async getEnrollmentHistory(courseMonitorId: string): Promise<EnrollmentSnapshot[]> {
    await this.delay(300);

    // Generate mock historical data
    const now = new Date();
    const snapshots: EnrollmentSnapshot[] = [];

    for (let i = 10; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 5 * 60 * 1000); // 5 minute intervals
      snapshots.push({
        id: String(i),
        courseMonitorId,
        totalSeats: 30,
        openSeats: Math.floor(Math.random() * 5),
        enrolledSeats: 30 - Math.floor(Math.random() * 5),
        waitlistTotal: 10,
        waitlistOpen: Math.floor(Math.random() * 3),
        status: Math.random() > 0.5 ? 'OPEN' : 'CLOSED',
        timestamp
      });
    }

    return snapshots;
  }

  async getNotificationPreferences(): Promise<NotificationPreferences> {
    await this.delay(300);
    return this.mockPreferences;
  }

  async updateNotificationPreferences(preferences: NotificationPreferences): Promise<NotificationPreferences> {
    await this.delay(300);
    this.mockPreferences = preferences;
    return this.mockPreferences;
  }

  async testNotification(type: 'email' | 'sms' | 'webhook'): Promise<{ success: boolean; message: string }> {
    await this.delay(1000);
    return {
      success: true,
      message: `Test ${type} notification sent successfully!`
    };
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
