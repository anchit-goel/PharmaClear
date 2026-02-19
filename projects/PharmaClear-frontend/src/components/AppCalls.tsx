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

const AppCalls = ({ openModal, setModalState }: AppCallsInterface) => {
  const [loading, setLoading] = useState<boolean>(false)
  const [contractInput, setContractInput] = useState<string>('')
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

  const sendAppCall = async () => {
    if (!activeAddress) {
      enqueueSnackbar('Please connect a wallet first', { variant: 'warning' })
      return
    }

    if (!contractInput.trim()) {
      enqueueSnackbar('Please enter a name to say hello to', { variant: 'warning' })
      return
    }

    setLoading(true)

    try {
      // Set the signer before making the call
      algorand.setDefaultSigner(transactionSigner)

      // Create the app client using the AppClient constructor with default sender
      const baseAppClient = algorand.client.getAppClientById(
        {
          appId: 1002n,
          appSpec: APP_SPEC,
          defaultSender: activeAddress,
        }
      )

      // Wrap with PharmaClearClient
      const appClient = new PharmaClearClient(baseAppClient)

      const response = await appClient.send.hello(
        { args: { name: contractInput } }
      )

      enqueueSnackbar(`Response from the contract: ${response.return}`, { variant: 'success' })
      setContractInput('')
    } catch (e: Error | unknown) {
      const error = e instanceof Error ? e : new Error('Unknown error')
      console.error('Contract call error:', error)
      enqueueSnackbar(`Error calling the contract: ${error.message}`, { variant: 'error' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <dialog id="appcalls_modal" className={`modal ${openModal ? 'modal-open' : ''} bg-slate-200`}>
      <form method="dialog" className="modal-box">
        <h3 className="font-bold text-lg">Say hello to your Algorand smart contract</h3>
        <br />
        <input
          type="text"
          placeholder="Provide input to hello function"
          className="input input-bordered w-full"
          value={contractInput}
          onChange={(e) => {
            setContractInput(e.target.value)
          }}
        />
        <div className="modal-action ">
          <button className="btn" onClick={() => setModalState(!openModal)}>
            Close
          </button>
          <button className={`btn`} onClick={sendAppCall}>
            {loading ? <span className="loading loading-spinner" /> : 'Send application call'}
          </button>
        </div>
      </form>
    </dialog>
  )
}

export default AppCalls
