// Backend URL
const API_URL = 'http://localhost:8000/api';

// ==================== GET REQUESTS ====================

export async function getAlerts(limit = 50) {
  try {
    const response = await fetch(`${API_URL}/alerts?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch alerts');
    return await response.json();
  } catch (error) {
    console.error('Error fetching alerts:', error);
    throw error;
  }
}

export async function getEvents(limit = 50) {
  try {
    const response = await fetch(`${API_URL}/events?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch events');
    return await response.json();
  } catch (error) {
    console.error('Error fetching events:', error);
    throw error;
  }
}

export async function getCameras() {
  try {
    const response = await fetch(`${API_URL}/cameras`);
    if (!response.ok) throw new Error('Failed to fetch cameras');
    return await response.json();
  } catch (error) {
    console.error('Error fetching cameras:', error);
    throw error;
  }
}

export async function getSystemStatus() {
  try {
    const response = await fetch(`${API_URL}/status`);
    if (!response.ok) throw new Error('Failed to fetch status');
    return await response.json();
  } catch (error) {
    console.error('Error fetching system status:', error);
    throw error;
  }
}

// ==================== POST REQUESTS ====================

export async function createAlert(alertData) {
  try {
    const response = await fetch(`${API_URL}/alerts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(alertData)
    });
    if (!response.ok) throw new Error('Failed to create alert');
    return await response.json();
  } catch (error) {
    console.error('Error creating alert:', error);
    throw error;
  }
}

export async function uploadVideo(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_URL}/upload/video`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) throw new Error('Failed to upload video');
    return await response.json();
  } catch (error) {
    console.error('Error uploading video:', error);
    throw error;
  }
}

// ==================== DELETE REQUESTS ====================

export async function clearAllAlerts() {
  try {
    const response = await fetch(`${API_URL}/alerts`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to clear alerts');
    return await response.json();
  } catch (error) {
    console.error('Error clearing alerts:', error);
    throw error;
  }
}