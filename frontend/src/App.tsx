import { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Plus, Bell, BookOpen, RefreshCw } from 'lucide-react';
import { CourseCard } from './components/CourseCard';
import { AddCourseModal } from './components/AddCourseModal';
import { NotificationSettings } from './components/NotificationSettings';
import { api, type MonitoredCourse } from './services/api';

type Tab = 'courses' | 'notifications';

function App() {
  const [courses, setCourses] = useState<MonitoredCourse[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('courses');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await api.getMonitoredCourses();
      setCourses(data);
    } catch (error) {
      toast.error('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const handleAddCourse = async (course: Omit<MonitoredCourse, 'id' | 'createdAt' | 'lastChecked'>) => {
    try {
      const newCourse = await api.addMonitoredCourse(course);
      setCourses([...courses, newCourse]);
      toast.success(`Added ${course.subject} ${course.courseNumber} to monitoring`);
    } catch (error) {
      toast.error('Failed to add course');
    }
  };

  const handleRemoveCourse = async (id: string) => {
    try {
      await api.removeMonitoredCourse(id);
      setCourses(courses.filter(c => c.id !== id));
      toast.success('Course removed from monitoring');
    } catch (error) {
      toast.error('Failed to remove course');
    }
  };

  const handleToggleActive = async (id: string, active: boolean) => {
    try {
      const updated = await api.updateMonitoredCourse(id, { active });
      setCourses(courses.map(c => c.id === id ? updated : c));
      toast.success(active ? 'Monitoring resumed' : 'Monitoring paused');
    } catch (error) {
      toast.error('Failed to update course');
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await loadCourses();
      toast.success('Courses refreshed');
    } catch (error) {
      toast.error('Failed to refresh courses');
    } finally {
      setRefreshing(false);
    }
  };

  const activeCourses = courses.filter(c => c.active);
  const pausedCourses = courses.filter(c => !c.active);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#0f172a', color: '#e2e8f0' }}>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e293b',
            color: '#e2e8f0',
            border: '1px solid #334155',
          },
        }}
      />

      {/* Header */}
      <header style={{
        backgroundColor: '#1e293b',
        borderBottom: '1px solid #334155',
        padding: '1.5rem 2rem'
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '1.875rem', fontWeight: '700', color: '#f1f5f9', marginBottom: '0.5rem' }}>
            UW Madison Course Enrollment Checker
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '1rem' }}>
            Monitor course availability and get notified when seats open up
          </p>
        </div>
      </header>

      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem' }}>
        {/* Tabs */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          borderBottom: '1px solid #334155',
          marginBottom: '2rem'
        }}>
          <button
            onClick={() => setActiveTab('courses')}
            style={{
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderBottom: activeTab === 'courses' ? '2px solid #3b82f6' : 'none',
              backgroundColor: 'transparent',
              color: activeTab === 'courses' ? '#3b82f6' : '#94a3b8',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: activeTab === 'courses' ? '600' : '400'
            }}
          >
            <BookOpen size={20} />
            Monitored Courses ({courses.length})
          </button>
          <button
            onClick={() => setActiveTab('notifications')}
            style={{
              padding: '0.75rem 1.5rem',
              border: 'none',
              borderBottom: activeTab === 'notifications' ? '2px solid #3b82f6' : 'none',
              backgroundColor: 'transparent',
              color: activeTab === 'notifications' ? '#3b82f6' : '#94a3b8',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: activeTab === 'notifications' ? '600' : '400'
            }}
          >
            <Bell size={20} />
            Notification Settings
          </button>
        </div>

        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <>
            {/* Actions */}
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => setShowAddModal(true)}
                className="primary"
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Plus size={20} />
                Add Course to Monitor
              </button>
              <button
                onClick={handleRefresh}
                disabled={refreshing}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <RefreshCw size={20} className={refreshing ? 'spin' : ''} />
                Refresh
              </button>
            </div>

            {/* Course List */}
            {loading ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
                Loading courses...
              </div>
            ) : courses.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
                <BookOpen size={48} style={{ margin: '0 auto 1rem', color: '#475569' }} />
                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#cbd5e1', marginBottom: '0.5rem' }}>
                  No courses being monitored
                </h3>
                <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
                  Add your first course to start monitoring enrollment status
                </p>
                <button
                  onClick={() => setShowAddModal(true)}
                  className="primary"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <Plus size={20} />
                  Add Course
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                {/* Active Courses */}
                {activeCourses.length > 0 && (
                  <div>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '1rem' }}>
                      Active Monitoring ({activeCourses.length})
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' }}>
                      {activeCourses.map(course => (
                        <CourseCard
                          key={course.id}
                          course={course}
                          onRemove={handleRemoveCourse}
                          onToggleActive={handleToggleActive}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Paused Courses */}
                {pausedCourses.length > 0 && (
                  <div>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#64748b', marginBottom: '1rem' }}>
                      Paused ({pausedCourses.length})
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1rem' }}>
                      {pausedCourses.map(course => (
                        <CourseCard
                          key={course.id}
                          course={course}
                          onRemove={handleRemoveCourse}
                          onToggleActive={handleToggleActive}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div style={{ maxWidth: '800px' }}>
            <NotificationSettings />
          </div>
        )}
      </div>

      {/* Add Course Modal */}
      {showAddModal && (
        <AddCourseModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddCourse}
        />
      )}
    </div>
  );
}

export default App;
