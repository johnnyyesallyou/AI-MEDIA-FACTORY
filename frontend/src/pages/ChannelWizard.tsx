import { useState } from 'react';
import StrategyPreview from './StrategyPreview';
import { Wand2, CheckCircle, AlertCircle, Loader2, ArrowLeft, Sparkles } from 'lucide-react';
import { wizardAPI } from '../api/client';

type Step = 'input' | 'suggest' | 'validate' | 'creating' | 'done';

export default function ChannelWizard() {
  const [step, setStep] = useState<Step>('input');
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [suggestion, setSuggestion] = useState<any>(null);
  const [editableConfig, setEditableConfig] = useState<any>(null);
  const [validation, setValidation] = useState<any>(null);
  const [created, setCreated] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSuggest = async () => {
    try {
      setLoading(true);
      setError(null);
      const { data } = await wizardAPI.suggest({ name, description });
      setSuggestion(data);
      setEditableConfig(data);
      setStep('suggest');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (configOverride?: any) => {
    const cfg = configOverride || editableConfig || suggestion;
    if (!cfg) return;
    try {
      setLoading(true);
      setError(null);
      const config = {
        content_type: cfg.content_type,
        topic: cfg.topic,
        language: cfg.language,
        profile_key: cfg.profile_key,
        sources: cfg.sources,
        publishing_mode: cfg.publishing_mode,
        publishing_frequency: cfg.publishing_frequency,
      };
      const { data } = await wizardAPI.validate(config);
      setValidation(data);
      setStep('validate');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    const cfg = editableConfig || suggestion;
    if (!cfg) return;
    try {
      setLoading(true);
      setError(null);
      setStep('creating');
      const { data } = await wizardAPI.create({
        name,
        config: {
          content_type: cfg.content_type,
          topic: cfg.topic,
          language: cfg.language,
          profile_key: cfg.profile_key,
          sources: cfg.sources,
          publishing_mode: cfg.publishing_mode,
          publishing_frequency: cfg.publishing_frequency,
        },
      });
      setCreated(data);
      setStep('done');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
      setStep('validate');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setStep('input');
    setName('');
    setDescription('');
    setSuggestion(null);
    setValidation(null);
    setCreated(null);
    setError(null);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <Wand2 className="w-8 h-8 text-blue-400" />
        <div>
          <h1 className="text-3xl font-bold text-white">Channel Wizard</h1>
          <p className="text-gray-400 mt-1">AI-powered channel configuration</p>
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-700 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div className="text-red-200">{error}</div>
        </div>
      )}

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-6 text-sm">
        {['input', 'suggest', 'validate', 'done'].map((s, i) => {
          const order = ['input', 'suggest', 'validate', 'done'];
          const currentIdx = order.indexOf(step === 'creating' ? 'done' : step);
          const stepIdx = order.indexOf(s);
          const isActive = stepIdx === currentIdx;
          const isDone = stepIdx < currentIdx;
          return (
            <div key={s} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium
                ${isDone ? 'bg-green-600 text-white' : isActive ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-400'}`}>
                {isDone ? <CheckCircle className="w-4 h-4" /> : i + 1}
              </div>
              <span className={`${isActive ? 'text-white' : 'text-gray-500'}`}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </span>
              {i < 3 && <div className="w-8 h-px bg-gray-700 mx-1" />}
            </div>
          );
        })}
      </div>

      {/* Input step */}
      {step === 'input' && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Channel Name *</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., Манга — новые главы"
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">Description (optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what this channel is about..."
              rows={3}
              className="w-full px-4 py-2 bg-gray-900 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            onClick={handleSuggest}
            disabled={!name || loading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
            Suggest Configuration
          </button>
        </div>
      )}

      {/* Suggest step — StrategyPreview */}
      {step === 'suggest' && editableConfig && (
        <StrategyPreview
          suggestion={editableConfig}
          onConfirm={(config) => {
            setEditableConfig(config);
            handleValidate(config);
          }}
          onCancel={() => {
            setStep('input');
            setSuggestion(null);
            setEditableConfig(null);
          }}
        />
      )}

      {/* Validate step */}
      {step === 'validate' && validation && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <h2 className="text-xl font-semibold text-white mb-4">Validation Result</h2>
          <div className={`mb-6 p-4 rounded-lg border ${validation.valid ? 'bg-green-900/20 border-green-800' : 'bg-red-900/20 border-red-800'}`}>
            <div className="flex items-center gap-2 mb-2">
              {validation.valid ? <CheckCircle className="w-5 h-5 text-green-400" /> : <AlertCircle className="w-5 h-5 text-red-400" />}
              <span className={`font-semibold ${validation.valid ? 'text-green-200' : 'text-red-200'}`}>
                {validation.valid ? 'Valid Configuration' : 'Invalid Configuration'}
              </span>
            </div>
            {validation.errors?.length > 0 && (
              <ul className="list-disc list-inside text-sm text-red-300 mt-2">
                {validation.errors.map((e: string, i: number) => <li key={i}>{e}</li>)}
              </ul>
            )}
            {validation.warnings?.length > 0 && (
              <ul className="list-disc list-inside text-sm text-yellow-300 mt-2">
                {validation.warnings.map((w: string, i: number) => <li key={i}>{w}</li>)}
              </ul>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setStep('suggest')}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
            {validation.valid && (
              <button
                onClick={handleCreate}
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-700"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                Create Channel
              </button>
            )}
          </div>
        </div>
      )}

      {/* Creating step */}
      {step === 'creating' && (
        <div className="bg-gray-800 rounded-lg p-12 border border-gray-700 text-center">
          <Loader2 className="w-12 h-12 text-blue-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-300">Creating channel...</p>
        </div>
      )}

      {/* Done step */}
      {step === 'done' && created && (
        <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
          <div className="text-center mb-6">
            <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-white mb-2">Channel Created!</h2>
            <p className="text-gray-400">{created.name} is ready to use</p>
          </div>
          <div className="space-y-2 mb-6">
            <InfoRow label="ID" value={created.id} mono />
            <InfoRow label="Platform" value={created.platform} />
            <InfoRow label="Profile" value={created.profile_key} />
            <InfoRow label="Schedule" value={created.schedule_cron} />
          </div>
          <div className="flex gap-2">
            <button
              onClick={reset}
              className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
            >
              Create Another
            </button>
            <a
              href="/channels"
              className="flex-1 flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Go to Channels
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

function InfoRow({ label, value, color, mono }: { label: string; value: string; color?: string; mono?: boolean }) {
  return (
    <div className="flex items-center justify-between p-3 bg-gray-900 rounded">
      <span className="text-gray-400 text-sm">{label}:</span>
      <span className={`${mono ? 'font-mono text-xs' : ''} ${
        color === 'green' ? 'text-green-400' : 'text-blue-300'
      }`}>{value}</span>
    </div>
  );
}