import type { MonitoredCourse } from '../services/api';
import { Clock, BookOpen, X, Play, Pause } from 'lucide-react';

interface CourseCardProps {
  course: MonitoredCourse;
  onRemove: (id: string) => void;
  onToggleActive: (id: string, active: boolean) => void;
}

export function CourseCard({ course, onRemove, onToggleActive }: CourseCardProps) {
  const formatInterval = (ms: number) => {
    const minutes = Math.floor(ms / 60000);
    return `${minutes} min`;
  };

  const formatLastChecked = (date?: Date) => {
    if (!date) return 'Never';
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#f1f5f9', marginBottom: '0.5rem' }}>
            {course.subject} {course.courseNumber}
          </h3>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <span className={`badge ${course.active ? 'open' : 'closed'}`}>
              {course.active ? 'Active' : 'Paused'}
            </span>
            <span style={{ fontSize: '0.875rem', color: '#94a3b8' }}>
              Term: {course.term}
            </span>
          </div>
        </div>
        <button
          onClick={() => onRemove(course.id)}
          className="danger"
          style={{ padding: '0.5rem' }}
          title="Remove course"
        >
          <X size={18} />
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#cbd5e1' }}>
          <BookOpen size={16} />
          <span style={{ fontSize: '0.875rem' }}>
            Sections: {course.sections.join(', ')}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#cbd5e1' }}>
          <Clock size={16} />
          <span style={{ fontSize: '0.875rem' }}>
            Check every {formatInterval(course.checkInterval)} • Last: {formatLastChecked(course.lastChecked)}
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', fontSize: '0.875rem', marginBottom: '1rem' }}>
        <span style={{ color: course.notifyOnOpen ? '#10b981' : '#64748b' }}>
          {course.notifyOnOpen ? '✓' : '✗'} Notify on open
        </span>
        <span style={{ color: '#475569' }}>•</span>
        <span style={{ color: course.notifyOnWaitlist ? '#10b981' : '#64748b' }}>
          {course.notifyOnWaitlist ? '✓' : '✗'} Notify on waitlist
        </span>
      </div>

      <button
        onClick={() => onToggleActive(course.id, !course.active)}
        style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
      >
        {course.active ? <Pause size={16} /> : <Play size={16} />}
        {course.active ? 'Pause Monitoring' : 'Resume Monitoring'}
      </button>
    </div>
  );
}
