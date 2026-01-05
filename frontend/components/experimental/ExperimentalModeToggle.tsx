/**
 * EXPERIMENTAL MODE TOGGLE
 * 
 * Persistent UI element visible on all pages
 * Allows user to access experimental trading mode
 * 
 * ⚠️ WARNING: Personal use only. Not SEBI compliant.
 */

'use client';

import React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function ExperimentalModeToggle() {
  const router = useRouter();
  const pathname = usePathname();
  const [showWarning, setShowWarning] = React.useState(false);

  // Hide toggle on experimental page itself
  if (pathname === '/experimental') {
    return null;
  }

  const handleEnterExperimental = () => {
    // Show warning first
    if (!showWarning) {
      setShowWarning(true);
      return;
    }

    // Navigate to experimental mode
    router.push('/experimental');
  };

  const handleDismissWarning = () => {
    setShowWarning(false);
  };

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Warning Modal */}
      {showWarning && (
        <div className="mb-4">
          <Alert variant="destructive" className="max-w-md">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription className="mt-2">
              <p className="font-bold mb-2">⚠️ EXPERIMENTAL MODE</p>
              <p className="text-sm mb-2">
                This mode generates trade predictions and biases.
                <br />
                <strong>NOT compliant with SEBI regulations.</strong>
                <br />
                Personal use only. You assume ALL responsibility.
              </p>
              <div className="flex gap-2 mt-3">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleDismissWarning}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={handleEnterExperimental}
                >
                  I Understand
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Toggle Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleEnterExperimental}
        className="bg-amber-100 hover:bg-amber-200 border-amber-400 text-amber-900"
      >
        <AlertTriangle className="w-4 h-4 mr-2" />
        Experimental Mode
      </Button>
    </div>
  );
}
