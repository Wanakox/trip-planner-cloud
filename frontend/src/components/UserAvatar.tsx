import { Avatar } from '@mui/material'
import { useQuery } from '@tanstack/react-query'

import { getCurrentUserPhoto } from '../api/user'
import type { UserProfile } from '../api/user'

function initials(user: UserProfile) {
  return `${user.name.trim()[0] ?? ''}${user.surname.trim()[0] ?? ''}`.toUpperCase()
}

export function UserAvatar({ user, size = 42 }: { user: UserProfile; size?: number }) {
  const photoQuery = useQuery({
    queryKey: ['current-user-photo', user.profile_photo],
    queryFn: getCurrentUserPhoto,
    enabled: Boolean(user.profile_photo),
    staleTime: Infinity,
  })
  return (
    <Avatar
      src={photoQuery.data}
      sx={{
        width: size,
        height: size,
        flexShrink: 0,
        bgcolor: 'primary.main',
        fontSize: size * 0.3,
        fontWeight: 800,
      }}
    >
      {initials(user)}
    </Avatar>
  )
}
