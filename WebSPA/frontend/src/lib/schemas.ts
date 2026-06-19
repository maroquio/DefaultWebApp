// Schemas Zod reutilizáveis para validação de formulários.
import { z } from 'zod'
import { Perfil } from './types'

/** Regras de senha forte (espelham validar_senha_forte do backend). */
export const senhaSchema = z
  .string()
  .min(8, 'A senha deve ter no mínimo 8 caracteres')
  .regex(/[A-Z]/, 'A senha deve conter pelo menos 1 letra maiúscula')
  .regex(/[a-z]/, 'A senha deve conter pelo menos 1 letra minúscula')
  .regex(/[0-9]/, 'A senha deve conter pelo menos 1 número')

export const emailSchema = z.string().min(1, 'Informe o e-mail').email('E-mail inválido')

export const loginSchema = z.object({
  email: emailSchema,
  senha: z.string().min(1, 'Informe a senha'),
})
export type LoginForm = z.infer<typeof loginSchema>

export const cadastroSchema = z
  .object({
    perfil: z.enum([Perfil.CLIENTE, Perfil.VENDEDOR], {
      message: 'Selecione um perfil',
    }),
    nome: z
      .string()
      .min(3, 'O nome deve ter no mínimo 3 caracteres')
      .max(100, 'O nome deve ter no máximo 100 caracteres'),
    email: emailSchema,
    senha: senhaSchema,
    confirmar_senha: z.string().min(1, 'Confirme a senha'),
  })
  .refine((d) => d.senha === d.confirmar_senha, {
    message: 'As senhas não coincidem',
    path: ['confirmar_senha'],
  })
export type CadastroForm = z.infer<typeof cadastroSchema>

const nomeUsuarioSchema = z
  .string()
  .min(3, 'O nome deve ter no mínimo 3 caracteres')
  .max(100, 'O nome deve ter no máximo 100 caracteres')

const perfilAdminSchema = z.enum([Perfil.ADMIN, Perfil.CLIENTE, Perfil.VENDEDOR], {
  message: 'Selecione um perfil',
})

export const adminUsuarioCadastroSchema = z.object({
  nome: nomeUsuarioSchema,
  email: emailSchema,
  senha: senhaSchema,
  perfil: perfilAdminSchema,
})
export type AdminUsuarioCadastroForm = z.infer<typeof adminUsuarioCadastroSchema>

export const adminUsuarioEdicaoSchema = z.object({
  nome: nomeUsuarioSchema,
  email: emailSchema,
  perfil: perfilAdminSchema,
})
export type AdminUsuarioEdicaoForm = z.infer<typeof adminUsuarioEdicaoSchema>

export const esqueciSenhaSchema = z.object({
  email: emailSchema,
})
export type EsqueciSenhaForm = z.infer<typeof esqueciSenhaSchema>

export const redefinirSenhaSchema = z
  .object({
    senha: senhaSchema,
    confirmar_senha: z.string().min(1, 'Confirme a senha'),
  })
  .refine((d) => d.senha === d.confirmar_senha, {
    message: 'As senhas não coincidem',
    path: ['confirmar_senha'],
  })
export type RedefinirSenhaForm = z.infer<typeof redefinirSenhaSchema>
