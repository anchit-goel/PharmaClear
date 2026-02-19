import { useWallet } from '@txnlab/use-wallet-react'
import { useSnackbar } from 'notistack'
import { useState, useMemo } from 'react'
import { PharmaClearClient, APP_SPEC } from '../contracts/PharmaClear'
import { getAlgodConfigFromViteEnvironment, getIndexerConfigFromViteEnvironment } from '../utils/network/getAlgoClientConfigs'
import { AlgorandClient } from '@algorandfoundation/algokit-utils'

interface AppCallsInterface {
  openModal: boolean
  setModalState: (value: boolean) => void
}

type MethodType = 'hello' | 'submit_claim' | 'verify_claim'

const AppCalls = ({ openModal, setModalState }: AppCallsInterface) => {
  const [loading, setLoading] = useState<boolean>(false)
  const [selectedMethod, setSelectedMethod] = useState<MethodType>('hello')
  const [nameInput, setNameInput] = useState<string>('')
  const [claimHashInput, setClaimHashInput] = useState<string>('')
  const { enqueueSnackbar } = useSnackbar()
  const { transactionSigner, activeAddress } = useWallet()

  const algodConfig = getAlgodConfigFromViteEnvironment()
  const indexerConfig = getIndexerConfigFromViteEnvironment()

  const algorand = useMemo(() => {
    const client = AlgorandClient.fromConfig({
      algodConfig,
      indexerConfig,
    })
    return client
  }, [algodConfig, indexerConfig])

  const callContract = async (method: MethodType) => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect a wallet first', { variant: 'warning' })
      return
    }

    if (method === 'hello' && !nameInput.trim()) {
      enqueueSnackbar('Please enter a name', { variant: 'warning' })
      return
    }

    if ((method === 'submit_claim' || method === 'verify_claim') && !claimHashInput.trim()) {
      enqueueSnackbar('Please enter a claim hash', { variant: 'warning' })
      return
    }

    setLoading(true)

    try {
      // Set the signer before making the call
      algorand.setDefaultSigner(transactionSigner)

      // Create the app client using the AppClient constructor with default sender
      const baseAppClient = algorand.client.getAppClientById(
        {
          appId: 1008n,
          appSpec: APP_SPEC,
          defaultSender: activeAddress,
        }
      )

      // Wrap with PharmaClearClient
      const appClient = new PharmaClearClient(baseAppClient)

      let response: { return?: string } | undefined

      if (method === 'hello') {
        response = await appClient.send.hello({ args: { name: nameInput } })
        setNameInput('')
      } else if (method === 'submit_claim') {
        response = await appClient.send.submitClaim({ args: { claimHash: claimHashInput } })
        setClaimHashInput('')
      } else if (method === 'verify_claim') {
        response = await appClient.send.verifyClaim({ args: { claimHash: claimHashInput } })
        setClaimHashInput('')
      }

      if (response?.return) {
        enqueueSnackbar(`Response: ${response.return}`, { variant: 'success' })
      }
    } catch (e: Error | unknown) {
      const error = e instanceof Error ? e : new Error('Unknown error')
      console.error('Contract call error:', error)
      enqueueSnackbar(`Error: ${error.message}`, { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <dialog id="appcalls_modal" className={`modal ${openModal ? 'modal-open' : ''} bg-slate-200`}>
      <form method="dialog" className="modal-box w-full max-w-2xl">
        <h3 className="font-bold text-lg mb-4">PharmaClear Contract Methods</h3>

        {/* Method selector tabs */}
        <div className="tabs mb-4">
          <button
            type="button"
            className={`tab tab-bordered ${selectedMethod === 'hello' ? 'tab-active' : ''}`}
            onClick={() => setSelectedMethod('hello')}
          >
            Hello
          </button>
          <button
            type="button"
            className={`tab tab-bordered ${selectedMethod === 'submit_claim' ? 'tab-active' : ''}`}
            onClick={() => setSelectedMethod('submit_claim')}
          >
            Submit Claim
          </button>
          <button
            type="button"
            className={`tab tab-bordered ${selectedMethod === 'verify_claim' ? 'tab-active' : ''}`}
            onClick={() => setSelectedMethod('verify_claim')}
          >
            Verify Claim
          </button>
        </div>

        {/* Hello method */}
        {selectedMethod === 'hello' && (
          <div className="space-y-3">
            <label className="label">
              <span className="label-text">Name</span>
            </label>
            <input
              type="text"
              placeholder="Enter a name to greet"
              className="input input-bordered w-full"
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
            />
            <p className="text-sm text-gray-600 mt-2">Greet someone by name using the hello method.</p>
          </div>
        )}

        {/* Submit Claim method */}
        {selectedMethod === 'submit_claim' && (
          <div className="space-y-3">
            <label className="label">
              <span className="label-text">Claim Hash</span>
            </label>
            <input
              type="text"
              placeholder="Enter claim hash (e.g., hash_abc123)"
              className="input input-bordered w-full"
              value={claimHashInput}
              onChange={(e) => setClaimHashInput(e.target.value)}
            />
            <p className="text-sm text-gray-600 mt-2">Submit a pharmaceutical claim with its hash fingerprint.</p>
          </div>
        )}

        {/* Verify Claim method */}
        {selectedMethod === 'verify_claim' && (
          <div className="space-y-3">
            <label className="label">
              <span className="label-text">Claim Hash</span>
            </label>
            <input
              type="text"
              placeholder="Enter claim hash to verify"
              className="input input-bordered w-full"
              value={claimHashInput}
              onChange={(e) => setClaimHashInput(e.target.value)}
            />
            <p className="text-sm text-gray-600 mt-2">Verify a pharmaceutical claim by its hash.</p>
          </div>
        )}

        {/* Action buttons */}
        <div className="modal-action mt-6">
          <button
            type="button"
            className="btn"
            onClick={() => setModalState(false)}
          >
            Close
          </button>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => callContract(selectedMethod)}
            disabled={loading}
          >
            {loading ? <span className="loading loading-spinner" /> : `Call ${selectedMethod}`}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default AppCalls
