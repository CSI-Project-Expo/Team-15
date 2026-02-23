import React, { useState } from 'react';

function Sidebar({ alerts = [], events = [] }) {

  const [alertsPanelOpen, setAlertsPanelOpen] = useState(true);
  const [eventsPanelOpen, setEventsPanelOpen] = useState(true);

  // Convert severity to CSS class
  const getSeverityClass = (severity) => {
  const map = {
    'critical': 'danger',
    'high': 'danger',
    'intrusion detected': 'danger',

    'medium': 'warning',
    'suspicious activity': 'warning',

    'low': 'caution',
    'motion detected': 'caution',

    'normal': 'normal',
    'system normal': 'normal'
  };

  return map[severity?.toLowerCase()] || 'normal';
};

  // Get icon color using CSS variables
  const getIconColor = (severity) => {
    const colors = {
      'danger': 'var(--accent-danger)',
      'warning': 'var(--accent-warning)',
      'caution': 'var(--accent-caution)',
      'normal': 'var(--accent-success)'
    };
    return colors[getSeverityClass(severity)];
  };

  return (
    <div className="sidebar">

      {/* ---------------- ALERTS PANEL (Custom Categories, no counts + System Normal) ---------------- */}
<div className={`panel ${!alertsPanelOpen ? 'collapsed' : ''}`}>
  <div
    className="panel-header dropdown-header"
    onClick={() => setAlertsPanelOpen(!alertsPanelOpen)}
  >
    ALERTS <span className="arrow">▼</span>
  </div>

  <div className="panel-content">
    {['intrusion', 'motion', 'suspicious'].map((type) => {
      // Check if events include this alert type
      const hasEvents = events.some(
        (event) =>
          (event.description || event.type || '').toLowerCase().includes(type)
      );

      if (!hasEvents) return null;

      const severityClassMap = {
        intrusion: 'danger',
        motion: 'warning',
        suspicious: 'caution',
      };
      const severityClass = severityClassMap[type] || 'normal';

      const displayType = type.charAt(0).toUpperCase() + type.slice(1);

      return (
        <div key={type} className={`alert-item ${severityClass}`}>
          <div className={`alert-icon ${severityClass}`}></div>
          <div className="alert-info">
            <div className="alert-type">
              {displayType}
            </div>
          </div>
        </div>
      );
    })}

    {/* Always show System Normal */}
    <div className="alert-item normal">
      <div className="alert-icon normal"></div>
      <div className="alert-info">
        <div className="alert-type">System Normal</div>
      </div>
    </div>
  </div>
</div>




      {/* ---------------- EVENT HISTORY PANEL ---------------- */}
      <div className={`panel ${!eventsPanelOpen ? 'collapsed' : ''}`}>
        <div
          className="panel-header dropdown-header"
          onClick={() => setEventsPanelOpen(!eventsPanelOpen)}
        >
          Event History <span className="arrow">▼</span>
        </div>

        <div className="panel-content event-scroll">
          {events.length > 0 ? (
            events.map((event, index) => (
              <div key={event.id || index} className="event-item">

                <div
                  className="event-icon"
                  style={{ background: getIconColor(event.severity) }}
                ></div>

                <div className="event-details">
                  <div className="event-description">
                    {event.description || event.type}
                  </div>
                </div>

                <div className={`event-severity severity-${event.severity?.toLowerCase()}`}>
                  {event.severity?.toUpperCase()}
                </div>

              </div>
            ))
          ) : (
            <div className="event-item">
              <div
                className="event-icon"
                style={{ background: 'var(--accent-success)' }}
              ></div>
              <div className="event-details">
                <div className="event-description">No events recorded</div>
              </div>
              <div className="event-severity severity-normal">NORMAL</div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}

export default Sidebar;
