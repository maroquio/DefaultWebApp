import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../lib/api'

interface FetchState<T> {
  data: T | null
  carregando: boolean
  erro: ApiError | null
  recarregar: () => void
}

// Hook genérico de leitura. `fn` deve ser estável (use useCallback) ou
// listar dependências em `deps`. Reexecuta quando `deps` muda.
export function useFetch<T>(fn: (signal: AbortSignal) => Promise<T>, deps: unknown[] = []): FetchState<T> {
  const [data, setData] = useState<T | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [erro, setErro] = useState<ApiError | null>(null)
  const [tick, setTick] = useState(0)

  const recarregar = useCallback(() => setTick((t) => t + 1), [])

  useEffect(() => {
    const controller = new AbortController()
    setCarregando(true)
    setErro(null)
    fn(controller.signal)
      .then((d) => {
        setData(d)
        setCarregando(false)
      })
      .catch((e) => {
        if ((e as Error).name === 'AbortError') return
        setErro(e instanceof ApiError ? e : new ApiError(0, String(e), 'internal_error'))
        setCarregando(false)
      })
    return () => controller.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick])

  return { data, carregando, erro, recarregar }
}
