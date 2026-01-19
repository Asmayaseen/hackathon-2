/**
 * Browser Notifications Hook
 *
 * Task: T021
 * Spec: specs/1-phase2-advanced-features/spec.md (US5)
 */
'use client';

import { useState, useEffect } from 'react';

export interface NotificationOptions {
  title: string;
  body?: string;
  icon?: string;
  tag?: string;
  onClick?: () => void;
}

export function useNotifications() {
  const [permission, setPermission] = useState<NotificationPermission>('default');
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    // Check if Notification API is supported
    if (typeof window !== 'undefined' && 'Notification' in window) {
      setIsSupported(true);
      setPermission(Notification.permission);
    }
  }, []);

  const requestPermission = async (): Promise<boolean> => {
    if (!isSupported) return false;

    try {
      const result = await Notification.requestPermission();
      setPermission(result);
      return result === 'granted';
    } catch (error) {
      console.error('Error requesting notification permission:', error);
      return false;
    }
  };

  const sendNotification = (options: NotificationOptions) => {
    if (!isSupported || permission !== 'granted') {
      console.warn('Notifications not available or permission denied');
      return null;
    }

    const notification = new Notification(options.title, {
      body: options.body,
      icon: options.icon || '/icon.png',
      tag: options.tag,
    });

    if (options.onClick) {
      notification.onclick = options.onClick;
    }

    return notification;
  };

  return {
    permission,
    isSupported,
    isGranted: permission === 'granted',
    isDenied: permission === 'denied',
    requestPermission,
    sendNotification,
  };
}
