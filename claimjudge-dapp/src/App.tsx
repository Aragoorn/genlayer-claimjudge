import { useState, useEffect } from 'react'
import { createClient, createAccount } from 'genlayer-js'
import { studionet } from 'genlayer-js/chains'
import { TransactionStatus } from 'genlayer-js/types'

const CONTRACT = '0x112f563F4DE1d981f0538A456Ea58C81cF93B73C'

const account = createAccount()
const client = createClient({
  chain: studionet,
  account,
})

export default function App() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [evidence, setEvidence] = useState('')
  const [claimId, setClaimId] = useState<number | null>(null)
  const [resolution, setResolution] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [status, setStatus] = useState('Initializing...')
  const [loading, setLoading] = useState(false)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    const init = async () => {
      try {
        await client.initializeConsensusSmartContract()
        setReady(true)
        setStatus('Ready')
        await loadStats()
      } catch (err: any) {
        console.error(err)
        setStatus('Initialization failed: ' + (err.message || err))
      }
    }
    init()
  }, [])

  const loadStats = async () => {
    try {
      const res = await client.readContract({
        address: CONTRACT,
        functionName: 'get_stats',
        args: [],
      })
      setStats(JSON.parse(res as string))
    } catch (err) {
      console.error('Stats error:', err)
    }
  }

  const createClaim = async () => {
    if (!title.trim() || !description.trim()) {
      alert('Title and Description are required')
      return
    }
    if (!ready) {
      alert('Client is not ready yet')
      return
    }

    setLoading(true)
    setStatus('Creating claim...')

    try {
      await client.initializeConsensusSmartContract()

      const hash = await client.writeContract({
        address: CONTRACT,
        functionName: 'create_claim',
        args: [title.trim(), description.trim(), evidence.trim() || ''],
        value: 0n,
      })

      setStatus('Waiting for transaction to be FINALIZED...')
      await client.waitForTransactionReceipt({
        hash,
        status: TransactionStatus.FINALIZED,
        retries: 120,
        interval: 3000,
      })

      const count = await client.readContract({
        address: CONTRACT,
        functionName: 'get_claim_count',
        args: [],
      })

      const newId = Number(count) - 1
      setClaimId(newId)
      setStatus(`Claim #${newId} created successfully!`)
      await loadStats()
    } catch (err: any) {
      console.error(err)
      setStatus('Error: ' + (err?.message || err?.shortMessage || JSON.stringify(err)))
    } finally {
      setLoading(false)
    }
  }

  const resolveClaim = async () => {
    if (claimId === null) return
    if (!ready) {
      alert('Client is not ready yet')
      return
    }

    setLoading(true)
    setStatus('AI is judging the claim... This can take 40–90 seconds')

    try {
      await client.initializeConsensusSmartContract()

      const hash = await client.writeContract({
        address: CONTRACT,
        functionName: 'resolve_claim',
        args: [claimId],
        value: 0n,
      })

      setStatus('Waiting for FINALIZED (AI consensus in progress)...')
      await client.waitForTransactionReceipt({
        hash,
        status: TransactionStatus.FINALIZED,
        retries: 180,
        interval: 4000,
      })

      const res = await client.readContract({
        address: CONTRACT,
        functionName: 'get_resolution',
        args: [claimId],
      })

      const parsed = JSON.parse(res as string)
      setResolution(parsed)
      setStatus('Resolved successfully!')
      await loadStats()
    } catch (err: any) {
      console.error(err)
      setStatus('Error: ' + (err?.message || err?.shortMessage || JSON.stringify(err)))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
          ClaimJudge
        </h1>
        <p className="text-gray-300 mt-2">AI-Powered Decentralized Claim Resolver on GenLayer</p>
        <p className="text-xs text-gray-500 mt-1 break-all">{CONTRACT}</p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          <div className="bg-white/5 rounded-2xl p-4 text-center border border-white/10">
            <div className="text-2xl font-bold">{stats.total_claims}</div>
            <div className="text-sm text-gray-400">Total</div>
          </div>
          <div className="bg-white/5 rounded-2xl p-4 text-center border border-white/10">
            <div className="text-2xl font-bold text-green-400">{stats.resolved_claims}</div>
            <div className="text-sm text-gray-400">Resolved</div>
          </div>
          <div className="bg-white/5 rounded-2xl p-4 text-center border border-white/10">
            <div className="text-2xl font-bold text-yellow-400">{stats.open_claims}</div>
            <div className="text-sm text-gray-400">Open</div>
          </div>
        </div>
      )}

      {/* Create Claim */}
      <div className="bg-white/5 rounded-2xl p-6 border border-white/10 mb-6">
        <h2 className="text-xl font-semibold mb-4">Create Claim</h2>
        <input
          className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 mb-3 focus:outline-none focus:border-indigo-500"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 mb-3 focus:outline-none focus:border-indigo-500"
          rows={4}
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 mb-4 focus:outline-none focus:border-indigo-500"
          placeholder="Evidence URLs (optional)"
          value={evidence}
          onChange={(e) => setEvidence(e.target.value)}
        />
        <button
          onClick={createClaim}
          disabled={loading || !ready}
          className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 py-3 rounded-xl font-semibold disabled:opacity-50 transition"
        >
          {loading ? 'Processing...' : 'Create Claim'}
        </button>
      </div>

      {/* Resolve */}
      {claimId !== null && (
        <div className="bg-white/5 rounded-2xl p-6 border border-white/10 mb-6">
          <h2 className="text-xl font-semibold mb-4">Claim #{claimId}</h2>
          <button
            onClick={resolveClaim}
            disabled={loading || !ready}
            className="w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 py-3 rounded-xl font-semibold disabled:opacity-50 transition"
          >
            {loading ? 'AI Judging...' : 'Resolve with AI'}
          </button>
        </div>
      )}

      {/* Result */}
      {resolution && (
        <div className="bg-white/5 rounded-2xl p-6 border border-green-500/40">
          <h2 className="text-xl font-semibold text-green-400 mb-4">AI Resolution</h2>
          <p>
            <span className="text-gray-400">Decision:</span>{' '}
            <strong className="text-green-400 text-lg">{resolution.decision}</strong>
          </p>
          <p className="mt-2">
            <span className="text-gray-400">Confidence:</span> {resolution.confidence}%
          </p>
          <p className="mt-2">
            <span className="text-gray-400">Summary:</span> {resolution.summary}
          </p>
          <p className="mt-2">
            <span className="text-gray-400">Reasoning:</span> {resolution.reasoning}
          </p>
        </div>
      )}

      {/* Status */}
      {status && (
        <p className="text-center mt-8 text-gray-300 text-sm">{status}</p>
      )}
    </div>
  )
}