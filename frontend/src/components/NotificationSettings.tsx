import { useState, useEffect } from 'react';
import { Mail, MessageSquare, Webhook, Send } from 'lucide-react';
import { api, type NotificationPreferences } from '../services/api';
import toast from 'react-hot-toast';

export function NotificationSettings() {
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email: { enabled: false, address: '' },
    sms: { enabled: false, phoneNumber: '' },
    webhook: { enabled: false, url: '' }
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      const prefs = await api.getNotificationPreferences();
      setPreferences(prefs);
    } catch (error) {
      toast.error('Failed to load notification preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.updateNotificationPreferences(preferences);
      toast.success('Notification preferences saved!');
    } catch (error) {
      toast.error('Failed to save preferences');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async (type: 'email' | 'sms' | 'webhook') => {
    const toastId = toast.loading(`Sending test ${type} notification...`);
    try {
      const result = await api.testNotification(type);
      if (result.success) {
        toast.success(result.message, { id: toastId });
      } else {
        toast.error(`Failed to send test ${type}`, { id: toastId });
      }
    } catch (error) {
      toast.error(`Failed to send test ${type}`, { id: toastId });
    }
  };

  if (loading) {
    return <div style={{ color: '#94a3b8' }}>Loading preferences...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Email */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <Mail size={24} color="#3b82f6" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>Email Notifications</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={preferences.email?.enabled || false}
              onChange={(e) => setPreferences({
                ...preferences,
                email: { ...preferences.email!, enabled: e.target.checked }
              })}
            />
            <span style={{ color: '#cbd5e1' }}>Enable email notifications</span>
          </label>

          {preferences.email?.enabled && (
            <>
              <input
                type="email"
                value={preferences.email.address}
                onChange={(e) => setPreferences({
                  ...preferences,
                  email: { ...preferences.email!, address: e.target.value }
                })}
                placeholder="your.email@wisc.edu"
                style={{ width: '100%' }}
              />
              <button
                onClick={() => handleTest('email')}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Send size={16} />
                Send Test Email
              </button>
            </>
          )}
        </div>
      </div>

      {/* SMS */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <MessageSquare size={24} color="#10b981" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>SMS Notifications</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={preferences.sms?.enabled || false}
              onChange={(e) => setPreferences({
                ...preferences,
                sms: { ...preferences.sms!, enabled: e.target.checked }
              })}
            />
            <span style={{ color: '#cbd5e1' }}>Enable SMS notifications</span>
          </label>

          {preferences.sms?.enabled && (
            <>
              <input
                type="tel"
                value={preferences.sms.phoneNumber}
                onChange={(e) => setPreferences({
                  ...preferences,
                  sms: { ...preferences.sms!, phoneNumber: e.target.value }
                })}
                placeholder="+1 (234) 567-8900"
                style={{ width: '100%' }}
              />
              <button
                onClick={() => handleTest('sms')}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Send size={16} />
                Send Test SMS
              </button>
            </>
          )}
        </div>
      </div>

      {/* Webhook */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <Webhook size={24} color="#a855f7" />
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: '#f1f5f9' }}>Webhook</h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={preferences.webhook?.enabled || false}
              onChange={(e) => setPreferences({
                ...preferences,
                webhook: { ...preferences.webhook!, enabled: e.target.checked }
              })}
            />
            <span style={{ color: '#cbd5e1' }}>Enable webhook notifications</span>
          </label>

          {preferences.webhook?.enabled && (
            <>
              <input
                type="url"
                value={preferences.webhook.url}
                onChange={(e) => setPreferences({
                  ...preferences,
                  webhook: { ...preferences.webhook!, url: e.target.value }
                })}
                placeholder="https://your-webhook-url.com/notify"
                style={{ width: '100%' }}
              />
              <button
                onClick={() => handleTest('webhook')}
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Send size={16} />
                Test Webhook
              </button>
            </>
          )}
        </div>
      </div>

      <button
        onClick={handleSave}
        disabled={saving}
        className="primary"
        style={{ width: '100%', padding: '0.75rem' }}
      >
        {saving ? 'Saving...' : 'Save Preferences'}
      </button>
    </div>
  );
}
