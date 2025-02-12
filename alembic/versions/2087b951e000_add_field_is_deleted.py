"""ADD Field : is_deleted

Revision ID: 2087b951e000
Revises: f78fa2fa9681
Create Date: 2025-02-12 10:25:12.917488
"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2087b951e000"
down_revision: Union[str, None] = "f78fa2fa9681"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new column 'is_deleted' to 'users' table
    op.add_column("users", sa.Column("is_deleted", sa.Boolean(), nullable=True))

    # Add the trigger function for soft delete
    op.execute(
        """
        CREATE OR REPLACE FUNCTION "public"._pgtrigger_should_ignore(
            trigger_name NAME
        )
        RETURNS BOOLEAN AS $$
            DECLARE
                _pgtrigger_ignore TEXT[];
                _result BOOLEAN;
            BEGIN
                BEGIN
                    SELECT INTO _pgtrigger_ignore
                        CURRENT_SETTING('pgtrigger.ignore');
                    EXCEPTION WHEN OTHERS THEN
                END;
                IF _pgtrigger_ignore IS NOT NULL THEN
                    SELECT trigger_name = ANY(_pgtrigger_ignore)
                    INTO _result;
                    RETURN _result;
                ELSE
                    RETURN FALSE;
                END IF;
            END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Soft Delete 트리거 함수 작성
    op.execute(
        """
        CREATE OR REPLACE FUNCTION pgtrigger_soft_delete_78625()
        RETURNS TRIGGER AS $$
            BEGIN
                IF ("public"._pgtrigger_should_ignore(TG_NAME) IS TRUE) THEN
                    IF (TG_OP = 'DELETE') THEN
                        RETURN OLD;
                    ELSE
                        RETURN NEW;
                    END IF;
                END IF;
                IF (OLD.is_deleted IS TRUE) THEN
                    RETURN OLD;
                END IF;
                UPDATE "users" SET is_active = FALSE, is_deleted = TRUE, deleted_at = now()
                WHERE "id" = OLD."id" AND is_deleted = FALSE;
                RETURN NULL;
            END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Soft delete trigger 생성
    op.execute(
        """
        DROP TRIGGER IF EXISTS pgtrigger_soft_delete_78625 ON "users";
        CREATE TRIGGER pgtrigger_soft_delete_78625
            BEFORE DELETE ON "users"
            FOR EACH ROW
            EXECUTE PROCEDURE pgtrigger_soft_delete_78625();
        COMMENT ON TRIGGER pgtrigger_soft_delete_78625 ON "users" IS 'Soft delete trigger for users';
    """
    )


def downgrade() -> None:
    # Drop the trigger and the function if downgrading
    op.execute(
        """
        DROP TRIGGER IF EXISTS pgtrigger_soft_delete_78625 ON "users";
    """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS pgtrigger_soft_delete_78625();
    """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS "public"._pgtrigger_should_ignore();
    """
    )

    # Drop the 'is_deleted' column
    op.drop_column("users", "is_deleted")
