'use client';

import { Bell } from 'lucide-react';
import { useState } from 'react';
import { Button } from './ui/button';

export function NotificationBell() {
  const [notificationCount] = useState(3); // Placeholder

  return (
    <div className="relative" data-tour="notifications">
      <Button variant="ghost" size="sm" className="relative">
        <Bell className="w-5 h-5" />
        {notificationCount > 0 && (
          <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
            {notificationCount > 9 ? '9+' : notificationCount}
          </span>
        )}
      </Button>
    </div>
  );
}
