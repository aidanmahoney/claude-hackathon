import { useState } from 'react';
import { X } from 'lucide-react';
import type { MonitoredCourse } from '../services/api';

interface AddCourseModalProps {
  onClose: () => void;
  onAdd: (course: Omit<MonitoredCourse, 'id' | 'createdAt' | 'lastChecked'>) => void;
}

export function AddCourseModal({ onClose, onAdd }: AddCourseModalProps) {
  const [formData, setFormData] = useState({
    term: '',
    subject: '',
    courseNumber: '',
    sections: '',
    notifyOnOpen: true,
    notifyOnWaitlist: false,
    checkInterval: 300000,
    active: true
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const sectionsArray = formData.sections
      .split(',')
      .map(s => s.trim())
      .filter(s => s.length > 0);

    onAdd({
      term: formData.term,
      subject: formData.subject.toUpperCase(),
      courseNumber: formData.courseNumber,
      sections: sectionsArray,
      notifyOnOpen: formData.notifyOnOpen,
      notifyOnWaitlist: formData.notifyOnWaitlist,
      checkInterval: formData.checkInterval,
      active: formData.active
    });

    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem'
    }}>
      <div style={{
        backgroundColor: '#1e293b',
        borderRadius: '12px',
        padding: '2rem',
        maxWidth: '500px',
        width: '100%',
        maxHeight: '90vh',
        overflow: 'auto',
        border: '1px solid #334155'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '600', color: '#f1f5f9' }}>
            Add Course to Monitor
          </h2>
          <button onClick={onClose} style={{ padding: '0.5rem' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#cbd5e1', fontSize: '0.875rem' }}>
              Term (e.g., 1252)
            </label>
            <input
              type="text"
              value={formData.term}
              onChange={(e) => setFormData({ ...formData, term: e.target.value })}
              required
              placeholder="1252"
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#cbd5e1', fontSize: '0.875rem' }}>
              Subject (e.g., COMP SCI)
            </label>
            <input
              type="text"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              required
              placeholder="COMP SCI"
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#cbd5e1', fontSize: '0.875rem' }}>
              Course Number (e.g., 400)
            </label>
            <input
              type="text"
              value={formData.courseNumber}
              onChange={(e) => setFormData({ ...formData, courseNumber: e.target.value })}
              required
              placeholder="400"
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#cbd5e1', fontSize: '0.875rem' }}>
              Sections (comma-separated, e.g., 001, 002)
            </label>
            <input
              type="text"
              value={formData.sections}
              onChange={(e) => setFormData({ ...formData, sections: e.target.value })}
              required
              placeholder="001, 002"
              style={{ width: '100%' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', color: '#cbd5e1', fontSize: '0.875rem' }}>
              Check Interval
            </label>
            <select
              value={formData.checkInterval}
              onChange={(e) => setFormData({ ...formData, checkInterval: Number(e.target.value) })}
              style={{ width: '100%' }}
            >
              <option value={180000}>3 minutes</option>
              <option value={300000}>5 minutes</option>
              <option value={600000}>10 minutes</option>
              <option value={900000}>15 minutes</option>
            </select>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.notifyOnOpen}
                onChange={(e) => setFormData({ ...formData, notifyOnOpen: e.target.checked })}
              />
              <span style={{ color: '#cbd5e1', fontSize: '0.875rem' }}>Notify when seats open</span>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={formData.notifyOnWaitlist}
                onChange={(e) => setFormData({ ...formData, notifyOnWaitlist: e.target.checked })}
              />
              <span style={{ color: '#cbd5e1', fontSize: '0.875rem' }}>Notify on waitlist availability</span>
            </label>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
            <button type="button" onClick={onClose} style={{ flex: 1 }}>
              Cancel
            </button>
            <button type="submit" className="primary" style={{ flex: 1 }}>
              Add Course
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
