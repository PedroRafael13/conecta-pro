#!/bin/bash

# Script para corrigir imports de notifications

echo "Corrigindo imports de notifications..."

# Preference service
sed -i "s|from '@/types/generated/notifications/notifications/notifications'|from '@/types/generated/notifications'|g" src/services/notifications/preference.service.ts
sed -i "s|BodyUpdateMyPreferences|PreferenceUpdate|g" src/services/notifications/preference.service.ts

# Push service
sed -i "s|from '@/types/generated/notifications/push-notifications/push-notifications'|from '@/types/generated/notifications'|g" src/services/notifications/push.service.ts
sed -i "s|BodyRegisterDevice|DeviceRegisterRequest|g" src/services/notifications/push.service.ts
sed -i "s|BodySendNotification as BodySendPush|SendPushRequest|g" src/services/notifications/push.service.ts
sed -i "s|BodySendPush|SendPushRequest|g" src/services/notifications/push.service.ts
sed -i "s|BodySubscribeToTopic|TopicSubscribeRequest|g" src/services/notifications/push.service.ts
sed -i "s|BodyUnsubscribeFromTopic|TopicUnsubscribeRequest|g" src/services/notifications/push.service.ts

# Intelligent service
sed -i "s|from '@/types/generated/notifications/intelligent-notifications/intelligent-notifications'|from '@/types/generated/notifications'|g" src/services/notifications/intelligent.service.ts

# Hooks - useNotifications
sed -i "s|from '@/types/generated/notifications/notifications/notifications'|from '@/types/generated/notifications'|g" src/hooks/notifications/useNotifications.ts
sed -i "s|BodySendNotification|SendNotificationRequest|g" src/hooks/notifications/useNotifications.ts

# Hooks - useTemplates
sed -i "s|from '@/types/generated/notifications/notifications/notifications'|from '@/types/generated/notifications'|g" src/hooks/notifications/useTemplates.ts
sed -i "s|BodyCreateTemplate|TemplateCreate|g" src/hooks/notifications/useTemplates.ts
sed -i "s|BodyUpdateTemplate|TemplateUpdate|g" src/hooks/notifications/useTemplates.ts

# Hooks - usePreferences
sed -i "s|from '@/types/generated/notifications/notifications/notifications'|from '@/types/generated/notifications'|g" src/hooks/notifications/usePreferences.ts
sed -i "s|BodyUpdateMyPreferences|PreferenceUpdate|g" src/hooks/notifications/usePreferences.ts

# Hooks - usePush
sed -i "s|from '@/types/generated/notifications/push-notifications/push-notifications'|from '@/types/generated/notifications'|g" src/hooks/notifications/usePush.ts
sed -i "s|BodyRegisterDevice|DeviceRegisterRequest|g" src/hooks/notifications/usePush.ts
sed -i "s|BodySendNotification|SendPushRequest|g" src/hooks/notifications/usePush.ts
sed -i "s|BodySubscribeToTopic|TopicSubscribeRequest|g" src/hooks/notifications/usePush.ts
sed -i "s|BodyUnsubscribeFromTopic|TopicUnsubscribeRequest|g" src/hooks/notifications/usePush.ts

echo "✅ Imports corrigidos!"
