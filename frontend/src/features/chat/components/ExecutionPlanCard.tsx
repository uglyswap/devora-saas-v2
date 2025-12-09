/**
 * ExecutionPlanCard Component
 * Agent: AI Chat Engineer
 *
 * Carte interactive pour afficher et gérer un plan d'exécution
 */

import React, { useState } from 'react';
import type { ExecutionPlan, ExecutionStep } from '../types/chat.types';
import { CodeDiff } from './CodeDiff';

export interface ExecutionPlanCardProps {
  plan: ExecutionPlan;
  onApprove?: () => void;
  onReject?: (reason?: string) => void;
  onModify?: (modifications: Partial<ExecutionPlan>) => void;
  className?: string;
}

export const ExecutionPlanCard: React.FC<ExecutionPlanCardProps> = ({
  plan,
  onApprove,
  onReject,
  onModify,
  className = '',
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showFileChanges, setShowFileChanges] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectDialog, setShowRejectDialog] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-700';
      case 'awaiting_confirmation':
        return 'bg-yellow-100 text-yellow-700';
      case 'approved':
        return 'bg-blue-100 text-blue-700';
      case 'executing':
        return 'bg-blue-500 text-white animate-pulse';
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'cancelled':
        return 'bg-gray-100 text-gray-500';
      case 'failed':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'in_progress':
        return '⟳';
      case 'failed':
        return '✗';
      case 'skipped':
        return '—';
      default:
        return '○';
    }
  };

  const handleReject = () => {
    onReject?.(rejectReason);
    setShowRejectDialog(false);
    setRejectReason('');
  };

  const completedSteps = plan.steps.filter((s) => s.status === 'completed').length;
  const totalSteps = plan.steps.length;
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <div className={`border rounded-lg bg-white shadow-sm ${className}`}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-lg text-gray-900">{plan.title}</h3>
            <p className="text-sm text-gray-600 mt-1">{plan.description}</p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(plan.status)}`}>
            {plan.status}
          </span>
        </div>

        {/* Progress Bar */}
        {plan.status === 'executing' && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>
                Progression: {completedSteps}/{totalSteps} étapes
              </span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Steps */}
      <div className="p-4">
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="flex items-center justify-between w-full text-left text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          <span>Étapes ({totalSteps})</span>
          <span className="transform transition-transform">{showDetails ? '▼' : '▶'}</span>
        </button>

        {showDetails && (
          <div className="mt-3 space-y-2">
            {plan.steps.map((step, index) => (
              <div
                key={step.id}
                className={`p-3 border rounded ${
                  step.status === 'in_progress'
                    ? 'border-blue-500 bg-blue-50'
                    : step.status === 'completed'
                    ? 'border-green-300 bg-green-50'
                    : step.status === 'failed'
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-200 bg-gray-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-lg">{getStepStatusIcon(step.status)}</span>
                  <div className="flex-1">
                    <span className="font-medium text-gray-900">
                      {index + 1}. {step.description}
                    </span>
                    {step.error && <p className="text-xs text-red-600 mt-1">Error: {step.error}</p>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      {plan.status === 'awaiting_confirmation' && (
        <div className="p-4 border-t bg-gray-50 flex items-center justify-end gap-3">
          <button
            onClick={() => setShowRejectDialog(true)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
          >
            Rejeter
          </button>
          <button
            onClick={onApprove}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
          >
            Approuver et Exécuter
          </button>
        </div>
      )}

      {/* Reject Dialog */}
      {showRejectDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Rejeter le plan</h3>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Raison du rejet (optionnel)..."
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
            <div className="flex items-center justify-end gap-3 mt-4">
              <button
                onClick={() => setShowRejectDialog(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
              >
                Annuler
              </button>
              <button
                onClick={handleReject}
                className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700"
              >
                Confirmer le rejet
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExecutionPlanCard;
