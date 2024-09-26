/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

export type TrackEventName =
  | 'ClickedRefresh'
  | 'ClientConnection'
  | 'LoadMoreCommits'
  | 'RunOperation'
  | 'TopLevelErrorShown'
  | 'UIEmptyState'
  | 'HeadCommitChanged'
  | 'AbortMergeOperation'
  | 'PullOperation'
  | 'PushOperation'
  | 'AddOperation'
  | 'AddRemoveOperation'
  | 'AlertShown'
  | 'AlertDismissed'
  | 'AmendMessageOperation'
  | 'AmendOperation'
  | 'AmendFileSubsetOperation'
  | 'AmendToOperation'
  | 'ArcPullOperation'
  | 'ArcStableForCommand'
  | 'ArcStableServerStablesCommand'
  | 'BulkRebaseOperation'
  | 'BookmarkCreateOperation'
  | 'BookmarkDeleteOperation'
  | 'CommitOperation'
  | 'CommitFileSubsetOperation'
  | 'ContinueMergeOperation'
  | 'CommitCloudStatusCommand'
  | 'CommitCloudListCommand'
  | 'CommitCloudSyncBackupStatusCommand'
  | 'CommitCloudChangeWorkspaceOperation'
  | 'CommitCloudCreateWorkspaceOperation'
  | 'CommitCloudSyncOperation'
  | 'CreateEmptyInitialCommit'
  | 'ClickSuggestedRebase'
  | 'ClickedConfigureExternalMergeTool'
  | 'DiscardOperation'
  | 'DiagnosticsConfirmationOpportunity'
  | 'DiagnosticsConfirmationAction'
  | 'EnterMergeConflicts'
  | 'ExitMergeConflicts'
  | 'FetchPendingSloc'
  | 'FetchSloc'
  | 'ForgetOperation'
  | 'FoldOperation'
  | 'FillCommitMessage'
  | 'FocusChanged'
  | 'SetFocusMode'
  | 'GettingStartedInteraction'
  | 'GetSuggestedReviewers'
  | 'GetAlertsCommand'
  | 'AcceptSuggestedReviewer'
  | 'GenerateAICommitMessage'
  | 'GenerateAICommitMessageFunnelEvent'
  | 'GhStackSubmitOperation'
  | 'GotoOperation'
  | 'GoBackToOldISL'
  | 'GoBackToOldISLOnce'
  | 'GoBackToOldISLReason'
  | 'GraftOperation'
  | 'HideOperation'
  | 'ImportStackOperation'
  | 'LandModalOpen'
  | 'LandModalConfirm'
  | 'LandModalSuccess'
  | 'LandModalError'
  | 'LandModalUriLandShown'
  | 'LandModalCliLandShown'
  | 'LandRoadblockShown'
  | 'LandRoadblockContinue'
  | 'LandRoadblockContinueExternal'
  | 'LandSyncWarningShown'
  | 'LandSyncWarningChoseUseRemote'
  | 'LandSyncWarningChoseSyncLocal'
  | 'NopOperation'
  | 'PartialCommitOperation'
  | 'PartialAmendOperation'
  | 'PartialDiscardOperation'
  | 'PrSubmitOperation'
  | 'PullOperation'
  | 'PullRevOperation'
  | 'PurgeOperation'
  | 'RebaseKeepOperation'
  | 'RebaseAllDraftCommitsOperation'
  | 'RebaseOperation'
  | 'ConfirmDragAndDropRebase'
  | 'ResolveOperation'
  | 'AutoMarkResolvedOperation'
  | 'ResolveInExternalMergeToolOperation'
  | 'UsingExternalMergeTool'
  | 'RevertOperation'
  | 'RmOperation'
  | 'RunMergeDriversOperation'
  | 'SetConfigOperation'
  | 'ShelveOperation'
  | 'DeleteShelveOperation'
  | 'UnshelveOperation'
  | 'RunCommand'
  | 'StatusCommand'
  | 'SawStableLocation'
  | 'LogCommand'
  | 'LookupCommitsCommand'
  | 'LookupAllCommitChangedFilesCommand'
  | 'GetShelvesCommand'
  | 'GetConflictsCommand'
  | 'BlameCommand'
  | 'CatCommand'
  | 'DiffCommand'
  | 'FetchCommitTemplateCommand'
  | 'ImportStackCommand'
  | 'ExportStackCommand'
  | 'ExitMessageOutOfOrder'
  | 'ShowBugButtonNux'
  | 'StackEditMetrics'
  | 'StackEditChangeTab'
  | 'StackEditInlineSplitButton'
  | 'SplitOpenFromCommitContextMenu'
  | 'SplitOpenFromHeadCommit'
  | 'SplitOpenRangeSelector'
  | 'SuccessionsDetected'
  | 'BuggySuccessionDetected'
  | 'SyncDiffMessageMutation'
  | 'ConfirmSyncNewDiffNumber'
  | 'UncommitOperation'
  | 'JfSubmitOperation'
  | 'JfGetOperation'
  | 'OptimisticFilesStateForceResolved'
  | 'OptimisticCommitsStateForceResolved'
  | 'OptimisticConflictsStateForceResolved'
  | 'OptInToNewISLAgain'
  | 'OpenAllFiles'
  | 'QueueOperation'
  | 'QueryGraphQL'
  | 'UploadImage'
  | 'RunVSCodeCommand'
  | 'RageCommand'
  | 'RepoUrlCommand'
  | 'BlameLoaded'
  | 'VSCodeExtensionActivated'
  | 'UseCustomCommitMessageTemplate'
  | 'SlocCommand'
  | 'SplitSuggestionError'
  | 'SplitOpenFromSplitSuggestion'
  | 'PendingSlocCommand'
  | 'SplitSuggestionsDismissedForSevenDays';

export type TrackErrorName =
  | 'BlameError'
  | 'DiffFetchFailed'
  | 'EdenFsUnhealthy'
  | 'InvalidCwd'
  | 'InvalidCommand'
  | 'JfNotAuthenticated'
  | 'GhCliNotAuthenticated'
  | 'GhCliNotInstalled'
  | 'LandModalError'
  | 'TopLevelError'
  | 'FetchError'
  | 'RunOperationError'
  | 'RunCommandError'
  | 'RepositoryError'
  | 'SyncMessageError'
  | 'UploadImageError'
  | 'VSCodeCommandError'
  | 'VSCodeActivationError'
  | 'SplitSuggestionError';
