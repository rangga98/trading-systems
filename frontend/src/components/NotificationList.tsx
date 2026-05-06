import { useAppStore } from '../stores/appStore'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'
import { useEffect, useState } from 'react'

export function NotificationList() {
  const { notifications, removeNotification } = useAppStore()

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onRemove={removeNotification}
        />
      ))}
    </div>
  )
}

function NotificationItem({
  notification,
  onRemove,
}: {
  notification: any
  onRemove: (id: string) => void
}) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onRemove(notification.id), 300)
    }, notification.duration || 5000)

    return () => clearTimeout(timer)
  }, [notification.id, notification.duration, onRemove])

  const typeStyles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  }

  const icons = {
    success: <CheckCircle className="h-5 w-5" />,
    error: <AlertCircle className="h-5 w-5" />,
    warning: <AlertTriangle className="h-5 w-5" />,
    info: <Info className="h-5 w-5" />,
  }

  return (
    <div
      className={`pointer-events-auto flex items-start gap-3 px-4 py-3 border rounded-lg shadow-lg transition-all duration-300 min-w-[300px] max-w-md ${
        isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
      } ${typeStyles[notification.type as keyof typeof typeStyles]}`}
    >
      <div className="shrink-0 mt-0.5">{icons[notification.type as keyof typeof icons]}</div>
      <div className="flex-1 text-sm font-medium">{notification.message}</div>
      <button
        onClick={() => {
          setIsVisible(false)
          setTimeout(() => onRemove(notification.id), 300)
        }}
        className="shrink-0 hover:opacity-70 transition-opacity"
      >
        <X className="h-5 w-5" />
      </button>
    </div>
  )
}
