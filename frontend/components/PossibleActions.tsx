import { motion } from "framer-motion";
import { CheckCircle, XCircle, Play, PauseCircle } from "lucide-react";

export interface Action {
  type: "entry" | "exit" | "hold" | "avoid";
  label: string;
  description: string;
  conditions: string[];
  enabled: boolean;
}

interface PossibleActionsProps {
  actions: Action[];
  onActionSelect?: (action: Action) => void;
}

export function PossibleActions({ actions, onActionSelect }: PossibleActionsProps) {
  const getActionIcon = (type: string) => {
    if (type === "entry") return <Play className="w-5 h-5 text-green-600" />;
    if (type === "exit") return <XCircle className="w-5 h-5 text-red-600" />;
    if (type === "hold") return <CheckCircle className="w-5 h-5 text-blue-600" />;
    return <PauseCircle className="w-5 h-5 text-amber-600" />;
  };

  const getActionColor = (type: string, enabled: boolean) => {
    if (!enabled) return "bg-muted border-muted-foreground/20 opacity-60";
    if (type === "entry") return "bg-green-50 dark:bg-green-900/10 border-green-300 dark:border-green-700 hover:bg-green-100 dark:hover:bg-green-900/20";
    if (type === "exit") return "bg-red-50 dark:bg-red-900/10 border-red-300 dark:border-red-700 hover:bg-red-100 dark:hover:bg-red-900/20";
    if (type === "hold") return "bg-blue-50 dark:bg-blue-900/10 border-blue-300 dark:border-blue-700 hover:bg-blue-100 dark:hover:bg-blue-900/20";
    return "bg-amber-50 dark:bg-amber-900/10 border-amber-300 dark:border-amber-700 hover:bg-amber-100 dark:hover:bg-amber-900/20";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-border rounded-xl p-6"
    >
      <h3 className="text-lg font-bold mb-4">Possible Actions</h3>
      <div className="space-y-3">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={() => action.enabled && onActionSelect?.(action)}
            disabled={!action.enabled}
            className={`w-full text-left border rounded-lg p-4 transition-all ${getActionColor(action.type, action.enabled)} ${
              action.enabled ? "cursor-pointer" : "cursor-not-allowed"
            }`}
          >
            <div className="flex items-start gap-3 mb-2">
              {getActionIcon(action.type)}
              <div className="flex-1">
                <div className="font-semibold mb-1">{action.label}</div>
                <p className="text-sm text-muted-foreground">{action.description}</p>
              </div>
            </div>
            {action.conditions.length > 0 && (
              <div className="ml-8 space-y-1">
                <div className="text-xs font-medium opacity-75">Conditions:</div>
                {action.conditions.map((condition, i) => (
                  <div key={i} className="text-xs opacity-75 flex items-start gap-1">
                    <span>•</span>
                    <span>{condition}</span>
                  </div>
                ))}
              </div>
            )}
          </button>
        ))}
      </div>
      <p className="text-xs text-muted-foreground mt-4 italic">
        No action is a valid decision. Trading discipline includes knowing when to stand aside.
      </p>
    </motion.div>
  );
}
