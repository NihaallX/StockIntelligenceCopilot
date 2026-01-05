import * as React from "react"

interface CollapsibleContextType {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const CollapsibleContext = React.createContext<CollapsibleContextType | undefined>(undefined)

export interface CollapsibleProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

export function Collapsible({ open: controlledOpen, onOpenChange, children }: CollapsibleProps) {
  const [uncontrolledOpen, setUncontrolledOpen] = React.useState(false)
  
  const open = controlledOpen !== undefined ? controlledOpen : uncontrolledOpen
  const setOpen = onOpenChange || setUncontrolledOpen
  
  return (
    <CollapsibleContext.Provider value={{ open, onOpenChange: setOpen }}>
      <div>
        {children}
      </div>
    </CollapsibleContext.Provider>
  )
}

export interface CollapsibleTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean
}

export function CollapsibleTrigger({ children, asChild, ...props }: CollapsibleTriggerProps) {
  const context = React.useContext(CollapsibleContext)
  
  if (!context) {
    throw new Error('CollapsibleTrigger must be used within a Collapsible')
  }
  
  if (asChild) {
    return React.cloneElement(children as React.ReactElement, {
      onClick: () => context.onOpenChange(!context.open),
    })
  }
  
  return (
    <button
      type="button"
      onClick={() => context.onOpenChange(!context.open)}
      {...props}
    >
      {children}
    </button>
  )
}

export interface CollapsibleContentProps extends React.HTMLAttributes<HTMLDivElement> {}

export function CollapsibleContent({ children, className = '', ...props }: CollapsibleContentProps) {
  const context = React.useContext(CollapsibleContext)
  
  if (!context) {
    throw new Error('CollapsibleContent must be used within a Collapsible')
  }
  
  if (!context.open) {
    return null
  }
  
  return (
    <div className={className} {...props}>
      {children}
    </div>
  )
}
