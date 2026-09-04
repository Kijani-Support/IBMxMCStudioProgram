import { useEffect, useState } from 'react';

export default function OfflineIndicator({ isOnline, pendingCount, isSyncing }) {
  const [showBanner, setShowBanner] = useState(false);
  const [hasInteracted, setHasInteracted] = useState(false);

  useEffect(() => {
    if (!hasInteracted) {
      setHasInteracted(true);
      return;
    }
    if (pendingCount > 0 || isSyncing) {
      setShowBanner(true);
    } else if (isOnline && !isSyncing && pendingCount === 0) {
      const timer = setTimeout(() => setShowBanner(false), 2000);
      return () => clearTimeout(timer);
    } else if (!isOnline) {
      setShowBanner(true);
    }
  }, [isOnline, isSyncing, pendingCount, hasInteracted]);

  if (!showBanner) return null;

  if (isSyncing) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 gradient-primary text-white text-center py-3 px-4 text-sm font-medium shadow-lg">
        <span className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Syncing {pendingCount} pending {pendingCount === 1 ? 'change' : 'changes'}...
        </span>
      </div>
    );
  }

  if (!isOnline) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-center py-3 px-4 text-sm font-medium shadow-lg">
        <span className="flex items-center justify-center gap-2">
          <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          You're offline — progress saved locally
          {pendingCount > 0 && ` (${pendingCount} pending sync)`}
        </span>
      </div>
    );
  }

  if (pendingCount > 0) {
    return (
      <div className="fixed top-0 left-0 right-0 z-50 bg-gradient-to-r from-amber-500 to-orange-500 text-white text-center py-3 px-4 text-sm font-medium shadow-lg">
        <span className="flex items-center justify-center gap-2">
          <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
          {pendingCount} {pendingCount === 1 ? 'change' : 'changes'} waiting to sync
        </span>
      </div>
    );
  }

  return null;
}
