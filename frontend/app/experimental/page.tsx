/**
 * EXPERIMENTAL MODE PAGE
 * 
 * Next.js page route for /experimental
 */

import ExperimentalModeView from '@/components/experimental/ExperimentalModeView';

export default function ExperimentalPage() {
  return <ExperimentalModeView />;
}

export const metadata = {
  title: '⚠️ Experimental Mode | Stock Intelligence',
  description: 'Personal trading experimentation mode - Not SEBI compliant',
};
