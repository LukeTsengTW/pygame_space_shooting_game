def swept_bullet_rect(bullet):
    previous_rect = getattr(bullet, "previous_rect", bullet.rect)
    return bullet.rect.union(previous_rect)


def bullet_hits_enemy(bullet, enemy):
    return bullet.rect.colliderect(enemy.rect) or swept_bullet_rect(bullet).colliderect(enemy.rect)
